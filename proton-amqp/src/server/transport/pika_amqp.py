"""CFX transport over AMQP 0-9-1 (pika) — for RabbitMQ 3.x brokers.

RabbitMQ 3.x speaks AMQP 0-9-1 natively; its bundled AMQP 1.0 plugin is
unreliable for *consuming* (a qpid-proton receiver attaches and is granted
credit but the broker delivers nothing). The rabbitmq-amqp-python-client
(the broker transport here) is worse — it hard-refuses any server below
4.0.0. So a machine that publishes CFX onto its own on-prem RabbitMQ 3.x
(e.g. Europlacer PROMON) can only be consumed over 0-9-1.

``PikaAmqp091Transport`` is the third :class:`CfxTransport`: a blocking
pika consumer on its own daemon thread. It binds an (optional) queue to an
(optional) fanout/exchange, consumes, normalises each body to a CFX dict
(reusing :meth:`MessageHandler._coerce_payload`) and hands it to
``on_message`` — identical seam to the broker/p2p transports, so the whole
downstream forward path (bus_inject live + signed audit) is unchanged.

Lazy import: ``pika`` is only imported inside :meth:`connect`, so a
deployment without a 0-9-1 endpoint never needs it installed.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Optional

from server.amqp.on_amqp_message import MessageHandler
from server.transport.base import CfxTransport, OnMessage

_logger = logging.getLogger(__name__)


class PikaAmqp091Transport(CfxTransport):
    """CFX ingest over AMQP 0-9-1 (pika BlockingConnection).

    Consumes ``queue`` on ``uri``. If ``exchange`` is given, the queue is
    (idempotently, passive-first) bound to it — matching the broker
    transport's exchange+queue shape. Reconnects with backoff on drop.

    Attributes:
        uri (str): amqp:// URI incl. vhost + credentials.
        queue (str): queue name to consume.
        exchange (Optional[str]): exchange to bind the queue to (fanout);
            empty ⇒ consume the queue as-is (already bound elsewhere).
        routing_key (str): binding key (ignored by fanout).
    """

    _RECONNECT_BACKOFF_S = 5.0

    def __init__(
            self,
            uri: str,
            queue: str,
            exchange: Optional[str] = None,
            routing_key: str = "",
            on_message: Optional[OnMessage] = None,
    ) -> None:
        super().__init__(on_message=on_message)
        self.uri = uri
        self.queue = queue
        self.exchange = exchange or ""
        self.routing_key = routing_key or ""
        self._thread: Optional[threading.Thread] = None
        self._connection = None
        self._channel = None
        self._running = False

    def connect(self) -> None:
        if not self.queue:
            _logger.error("Pika transport: 'queue' is required")
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._run, name=f"cfx-pika-{id(self)}", daemon=True)
        self._thread.start()

    def _run(self) -> None:
        import pika  # ленив import — само 0-9-1 endpoint го изисква

        params = pika.URLParameters(self.uri)
        # Разумни heartbeat/timeout-и за дълготраен consumer.
        params.heartbeat = 60
        params.blocked_connection_timeout = 30

        while self._running:
            try:
                self._connection = pika.BlockingConnection(params)
                self._channel = self._connection.channel()
                # Пасивно проверяваме че queue-то съществува (не декларираме
                # с чужди аргументи — конфигурира се от страната на брокера).
                self._channel.queue_declare(queue=self.queue, passive=True)
                if self.exchange:
                    try:
                        self._channel.queue_bind(
                            queue=self.queue, exchange=self.exchange,
                            routing_key=self.routing_key)
                    except Exception as exc:  # noqa: BLE001
                        _logger.warning(
                            "Pika transport: bind %s→%s failed (може вече да е "
                            "bound): %s", self.exchange, self.queue, exc)
                self._channel.basic_qos(prefetch_count=20)
                _logger.info(
                    "CFX pika[0-9-1] consuming queue=%s exchange=%s",
                    self.queue, self.exchange or "-")
                self._channel.basic_consume(
                    queue=self.queue, on_message_callback=self._on_pika_message,
                    auto_ack=False)
                self._channel.start_consuming()
            except Exception as exc:  # noqa: BLE001
                if self._running:
                    _logger.error(
                        "CFX pika transport error (reconnect in %ss): %s",
                        self._RECONNECT_BACKOFF_S, exc)
                    self._safe_close()
                    time.sleep(self._RECONNECT_BACKOFF_S)
            else:
                break
        self._safe_close()

    def _on_pika_message(self, channel, method, properties, body) -> None:
        try:
            payload = MessageHandler._coerce_payload(body)
            props = dict(getattr(properties, "headers", None) or {})
            if self.on_message is not None:
                self.on_message(payload, props)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as exc:  # noqa: BLE001 — логваме и nack-ваме (requeue)
            _logger.error("CFX pika forward error: %s", exc)
            try:
                channel.basic_nack(delivery_tag=method.delivery_tag,
                                   requeue=True)
            except Exception:  # noqa: BLE001
                pass

    def _safe_close(self) -> None:
        for obj in (self._channel, self._connection):
            try:
                if obj is not None and obj.is_open:
                    obj.close()
            except Exception:  # noqa: BLE001
                pass
        self._channel = None
        self._connection = None

    def disconnect(self) -> None:
        self._running = False
        # start_consuming() блокира в pika thread-а; добавяме stop чрез
        # thread-safe callback, ако връзката още е жива.
        conn = self._connection
        if conn is not None:
            try:
                conn.add_callback_threadsafe(self._stop_consuming)
            except Exception:  # noqa: BLE001
                self._safe_close()
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None

    def _stop_consuming(self) -> None:
        try:
            if self._channel is not None and self._channel.is_open:
                self._channel.stop_consuming()
        except Exception:  # noqa: BLE001
            pass

    @property
    def is_connected(self) -> bool:
        return (self._running and self._thread is not None
                and self._thread.is_alive())
