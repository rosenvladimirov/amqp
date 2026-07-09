import logging
import threading
from typing import Any, Dict, Optional

from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container

from server.amqp.on_amqp_message import MessageHandler
from server.transport.base import CfxTransport, OnMessage

_logger = logging.getLogger(__name__)


class _P2PReceiverHandler(MessagingHandler):
    """
    qpid-proton reactor handler for an AMQP 1.0 peer-to-peer CFX link.

    Unlike the broker transport there is no exchange/queue; the peer is addressed
    directly and messages flow over a link identified by its ``source`` address.
    Two modes are supported:

    * ``connect`` (default) — dial ``url`` and open a receiver on ``source``
      (the machine, or a router, acts as the server);
    * ``listen`` — bind ``url`` and accept inbound links (this process is the
      server the machine connects to).

    Every received message is normalized to a CFX ``dict`` (reusing
    :meth:`MessageHandler._coerce_payload`) and handed to ``on_message`` before
    the delivery is accepted.
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
            _logger.info(f"CFX P2P connected to {self._url} (source={self._source})")

    def on_message(self, event: Any) -> None:
        message: Message = event.message
        payload: Dict[str, Any] = MessageHandler._coerce_payload(message.body)
        properties: Dict[str, Any] = dict(message.properties or {})
        try:
            if self._on_message is not None:
                self._on_message(payload, properties)
            self.accept(event)
        except Exception as exc:  # noqa: BLE001 - логваме и reject-ваме
            _logger.error(f"CFX P2P forward error: {exc}")
            self.reject(event)

    def on_transport_error(self, event: Any) -> None:
        _logger.error(f"CFX P2P transport error: {event.transport.condition}")


class P2PTransport(CfxTransport):
    """
    CFX transport over raw AMQP 1.0 peer-to-peer (no broker).

    Runs a qpid-proton :class:`Container` on a dedicated daemon thread so several
    transports (broker and P2P) can run concurrently inside one host. Addressing
    is by link ``source``/``target`` rather than exchange/queue.

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
        self._handler = _P2PReceiverHandler(url, source, mode, on_message)
        self._container: Optional[Container] = None
        self._thread: Optional[threading.Thread] = None
        self._connected = False

    def connect(self) -> None:
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
