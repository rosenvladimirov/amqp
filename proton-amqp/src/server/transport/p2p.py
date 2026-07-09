from __future__ import annotations

import logging
import threading
from typing import Any, Optional

from server.amqp.on_amqp_message import MessageHandler
from server.transport.base import CfxTransport, OnMessage

_logger = logging.getLogger(__name__)

# python-qpid-proton е нужен САМО за този P2P транспорт (AMQP 1.0 без брокер).
# Импортва се МЪРЗЕЛИВО (вътре във фабриката/`connect()`), за да може
# broker-only станция да импортва `server.cfx_plugin` без инсталиран
# qpid-proton — broker пътят ползва rabbitmq-amqp-python-client.
_P2P_HANDLER_CLS = None


def _p2p_handler_cls():
    """Build (once) the qpid-proton ``MessagingHandler`` subclass.

    Дефинира се лениво, защото наследяването от ``MessagingHandler`` става
    при създаване на класа — ако беше на module top-level, самото import-ване
    на модула щеше да изисква qpid-proton. Викаме го чак при ``connect()``.
    """
    global _P2P_HANDLER_CLS
    if _P2P_HANDLER_CLS is not None:
        return _P2P_HANDLER_CLS

    from proton.handlers import MessagingHandler

    class _P2PReceiverHandler(MessagingHandler):
        """
        qpid-proton reactor handler for an AMQP 1.0 peer-to-peer CFX link.

        Unlike the broker transport there is no exchange/queue; the peer is
        addressed directly and messages flow over a link identified by its
        ``source`` address. Two modes are supported:

        * ``connect`` (default) — dial ``url`` and open a receiver on
          ``source`` (the machine, or a router, acts as the server);
        * ``listen`` — bind ``url`` and accept inbound links (this process is
          the server the machine connects to).

        Every received message is normalized to a CFX ``dict`` (reusing
        :meth:`MessageHandler._coerce_payload`) and handed to ``on_message``
        before the delivery is accepted.
        """

        def __init__(
                self,
                url: str,
                source: Optional[str] = None,
                mode: str = "connect",
                on_message: Optional[OnMessage] = None,
        ) -> None:
            super().__init__()
            self._url = url
            self._source = source
            self._mode = mode
            self._on_message = on_message
            self._acceptor = None
            self._connection = None

        def on_start(self, event: Any) -> None:
            container = event.container
            if self._mode == "listen":
                # Този процес е сървърът; машините/пиърите се свързват към нас.
                self._acceptor = container.listen(self._url)
                _logger.info(f"CFX P2P listening on {self._url}")
            else:
                self._connection = container.connect(self._url)
                container.create_receiver(self._connection, self._source)
                _logger.info(
                    f"CFX P2P connected to {self._url} (source={self._source})")

        def on_message(self, event: Any) -> None:
            message = event.message
            payload = MessageHandler._coerce_payload(message.body)
            properties = dict(message.properties or {})
            try:
                if self._on_message is not None:
                    self._on_message(payload, properties)
                self.accept(event)
            except Exception as exc:  # noqa: BLE001 - логваме и reject-ваме
                _logger.error(f"CFX P2P forward error: {exc}")
                self.reject(event)

        def on_transport_error(self, event: Any) -> None:
            _logger.error(
                f"CFX P2P transport error: {event.transport.condition}")

    _P2P_HANDLER_CLS = _P2PReceiverHandler
    return _P2P_HANDLER_CLS


class P2PTransport(CfxTransport):
    """
    CFX transport over raw AMQP 1.0 peer-to-peer (no broker).

    Runs a qpid-proton :class:`Container` on a dedicated daemon thread so
    several transports (broker and P2P) can run concurrently inside one host.
    Addressing is by link ``source``/``target`` rather than exchange/queue.

    The qpid-proton handler + :class:`Container` are built in :meth:`connect`
    (lazy import), so instantiating this transport — and importing the module
    — never requires python-qpid-proton until a P2P endpoint is actually
    brought up.

    Attributes:
        url (str): Peer URL to dial (``connect``) or bind (``listen``).
        source (Optional[str]): Receiver link source address.
        mode (str): ``"connect"`` (default) or ``"listen"``.
    """

    def __init__(
            self,
            url: str,
            source: Optional[str] = None,
            mode: str = "connect",
            on_message: Optional[OnMessage] = None,
    ) -> None:
        super().__init__(on_message=on_message)
        self.url = url
        self.source = source
        self.mode = mode
        self._handler = None
        self._container = None
        self._thread: Optional[threading.Thread] = None
        self._connected = False

    def connect(self) -> None:
        # Ленив proton import — само тук (и във фабриката на хендлъра).
        from proton.reactor import Container

        handler_cls = _p2p_handler_cls()
        self._handler = handler_cls(
            self.url, self.source, self.mode, self.on_message)
        self._container = Container(self._handler)
        self._thread = threading.Thread(
            target=self._run, name=f"cfx-p2p-{id(self)}", daemon=True
        )
        self._connected = True
        self._thread.start()

    def _run(self) -> None:
        try:
            self._container.run()
        except Exception as exc:  # noqa: BLE001 - контейнерът спира при stop()
            _logger.error(f"CFX P2P container stopped: {exc}")
        finally:
            self._connected = False

    def disconnect(self) -> None:
        self._connected = False
        if self._container is not None:
            try:
                self._container.stop()
            except Exception as exc:  # noqa: BLE001
                _logger.error(f"CFX P2P stop error: {exc}")
        if self._thread is not None:
            self._thread.join(timeout=5)

    @property
    def is_connected(self) -> bool:
        return self._connected and self._thread is not None and self._thread.is_alive()
