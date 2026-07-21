# Copyright 2024-2026 Rosen Vladimirov / Terraros Commerce Ltd.
# SPDX-License-Identifier: LGPL-3.0-or-later
import logging
import threading
from typing import Any, Dict, List, Optional

from server.transport.base import CfxTransport, OnMessage
from server.transport.broker import BrokerTransport
from server.transport.p2p import P2PTransport

_logger = logging.getLogger(__name__)


class CFXPlugin:
    """
    Embeddable façade for consuming CFX-IPC messages from one or more sources.

    :class:`CFXPlugin` is the entry point for hosting the CFX consumer inside
    another application (e.g. the ErpNet.FP proxy). Unlike the CLI ``main.py`` it
    is driven entirely by a plain ``dict`` configuration and never calls
    ``signal.pause()``: :meth:`start` brings every configured transport up on its
    own daemon thread and returns immediately, and :meth:`stop` tears them down.

    A single plugin instance drives several :class:`CfxTransport` endpoints
    concurrently, mixing broker (RabbitMQ/AMQP) and AMQP 1.0 peer-to-peer sources
    freely — every received CFX message is delivered to the ``on_message``
    forwarder as ``(cfx_payload, properties)``.

    Configuration shape::

        {
            "endpoints": [
                {"transport": "broker", "uri": "amqp://host:5672",
                 "queue": "cfx", "exchange": "CFXExchange",
                 "routing_key": "CFX.#"},
                {"transport": "p2p", "url": "amqp://machine:5672",
                 "source": "cfx/station1", "mode": "connect"},
            ]
        }

    A flat single-endpoint config is also accepted (a ``connection`` sub-dict, as
    produced from the INI loader, or the connection keys at the top level).

    Attributes:
        transports (List[CfxTransport]): The live transports created by
            :meth:`start`.
    """

    def __init__(self) -> None:
        self.transports: List[CfxTransport] = []
        self._threads: List[threading.Thread] = []
        self._on_message: Optional[OnMessage] = None
        self._started = False

    def start(self, config: Dict[str, Any], on_message: Optional[OnMessage] = None) -> None:
        """
        Build every configured transport and bring it up on a daemon thread.

        Args:
            config: The plugin configuration ``dict`` (see class docstring).
            on_message: Forwarder invoked with ``(cfx_payload, properties)`` for
                every received CFX message.

        Raises:
            ValueError: If the configuration yields no usable endpoint.
        """
        if self._started:
            _logger.warning("CFXPlugin already started; ignoring start()")
            return

        self._on_message = on_message
        self.transports = self._build_transports(config, on_message)
        if not self.transports:
            raise ValueError("CFXPlugin: no CFX endpoints in configuration")

        for transport in self.transports:
            thread = threading.Thread(
                target=self._connect_transport,
                args=(transport,),
                name=f"cfx-plugin-{id(transport)}",
                daemon=True,
            )
            thread.start()
            self._threads.append(thread)

        self._started = True
        _logger.info(f"CFXPlugin started with {len(self.transports)} endpoint(s)")

    def stop(self) -> None:
        """Disconnect every transport and join its worker thread."""
        for transport in self.transports:
            try:
                transport.disconnect()
            except Exception as exc:  # noqa: BLE001 - best-effort teardown
                _logger.error(f"CFXPlugin: error stopping transport: {exc}")
        for thread in self._threads:
            thread.join(timeout=5)
        self.transports = []
        self._threads = []
        self._started = False
        _logger.info("CFXPlugin stopped")

    @property
    def is_running(self) -> bool:
        """Whether the plugin has been started and not yet stopped."""
        return self._started

    @staticmethod
    def _connect_transport(transport: CfxTransport) -> None:
        try:
            transport.connect()
        except Exception as exc:  # noqa: BLE001 - логваме, не убиваме останалите
            _logger.error(f"CFXPlugin: transport connect failed: {exc}")

    def _build_transports(
            self,
            config: Dict[str, Any],
            on_message: Optional[OnMessage],
    ) -> List[CfxTransport]:
        """Instantiate a :class:`CfxTransport` per endpoint spec in ``config``."""
        specs = config.get("endpoints")
        if not specs:
            # Плосък single-endpoint конфиг: или вложена 'connection' секция
            # (както идва от INI loader-а), или ключовете директно най-горе.
            connection = config.get("connection", config)
            specs = [connection] if connection.get("uri") or connection.get("url") else []

        transports: List[CfxTransport] = []
        for spec in specs:
            transport = self._build_transport(spec, on_message)
            if transport is not None:
                transports.append(transport)
        return transports

    @staticmethod
    def _build_transport(
            spec: Dict[str, Any],
            on_message: Optional[OnMessage],
    ) -> Optional[CfxTransport]:
        """Build one transport from its spec dict, dispatching on ``transport``."""
        # По подразбиране е broker (текущият продукционен път); P2P/pika = явен избор.
        kind = (spec.get("transport") or "broker").lower()
        if kind in ("amqp091", "amqp0-9-1", "pika", "rabbit3", "broker091"):
            # AMQP 0-9-1 (RabbitMQ 3.x) — pika consumer.
            uri = spec.get("uri") or spec.get("url")
            queue = spec.get("queue") or spec.get("queue_name")
            if not uri or not queue:
                _logger.error("CFXPlugin: amqp091 endpoint needs 'uri' + 'queue'")
                return None
            from server.transport.pika_amqp import PikaAmqp091Transport
            return PikaAmqp091Transport(
                uri=uri,
                queue=queue,
                exchange=spec.get("exchange") or spec.get("exchange_name"),
                routing_key=spec.get("routing_key", ""),
                on_message=on_message,
            )
        if kind in ("p2p", "peer", "amqp1", "direct"):
            url = spec.get("url") or spec.get("uri")
            if not url:
                _logger.error("CFXPlugin: P2P endpoint missing 'url'")
                return None
            return P2PTransport(
                url=url,
                source=spec.get("source"),
                mode=spec.get("mode", "connect"),
                on_message=on_message,
            )

        uri = spec.get("uri") or spec.get("url")
        if not uri:
            _logger.error("CFXPlugin: broker endpoint missing 'uri'")
            return None
        return BrokerTransport(
            uri=uri,
            queue_name=spec.get("queue") or spec.get("queue_name"),
            routing_key=spec.get("routing_key"),
            exchange_name=spec.get("exchange") or spec.get("exchange_name"),
            ssl_config=spec.get("ssl_config"),
            on_message=on_message,
        )
