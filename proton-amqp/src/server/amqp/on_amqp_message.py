import gzip
import json
import logging
from typing import Any, Callable, Dict, Optional

from rabbitmq_amqp_python_client import AMQPMessagingHandler, Event
# I will improve it to add rags of plugs
from .message_processor import MessageProcessor

_logger = logging.getLogger(__name__)

# Type of the optional forwarder callback: (cfx_payload, amqp_properties) -> None
OnMessage = Callable[[Dict[str, Any], Dict[str, Any]], None]


def message_properties(message: Any) -> Dict[str, Any]:
    """Връща application properties на AMQP съобщение като plain dict.

    Vendored Message класът на rabbitmq-amqp-python-client излага само
    ``application_properties`` (НЯМА ``properties`` — достъпът гърми с
    AttributeError), докато raw proton.Message (P2P транспорта) ползва
    ``properties``. Този helper поддържа и двата типа.
    """
    props = getattr(message, "application_properties", None)
    if props is None:
        props = getattr(message, "properties", None)
    return dict(props or {})


class MessageHandler(AMQPMessagingHandler, MessageProcessor):
    """
    Handles CFX messages received via AMQP protocol.

    This class processes incoming AMQP messages, handles errors during message
    processing, and manages the state of processed data. It provides interfaces for
    retrieving processed data and assigning custom processing functions.

    An optional ``on_message`` forwarder callback may be supplied; when set it is
    invoked with ``(cfx_payload_dict, properties_dict)`` for every accepted
    message, immediately before ``delivery_context.accept()``. This is the seam
    used to embed the consumer inside another host (e.g. the ErpNet.FP proxy),
    which forwards the CFX event onward over its own links.
    """
    def __init__(self, on_message: Optional[OnMessage] = None):
        super().__init__()
        self._processed: Any = None
        self._published: Any = None
        self._client_id: str = ""
        self._on_message: Optional[OnMessage] = on_message

    def on_amqp_message(self, event: Event) -> None:
        """
        Handles the AMQP message received during an event. The method processes the
        event message and handles decoding errors as well as generic exceptions that
        may arise during processing. If an error occurs, the event is discarded to
        ensure proper delivery context handling.

        Args:
            event (Event): The event object containing the received AMQP message.

        Raises:
            json.JSONDecodeError: If there is an error decoding a JSON message.
            Exception: For any other processing errors encountered.

        Returns:
            None
        """
        props = message_properties(event.message)
        _logger.info(f"Message received from client: {props}")
        if not props.get('ClientId', None) == self._client_id:
            try:
                self._process_message(event.message)
                self._forward(event.message)
                self.delivery_context.accept(event)
            except json.JSONDecodeError:
                _logger.error("JSON Message Decoding Error")
                self.delivery_context.discard(event)
            except Exception as e:
                _logger.error(f"Message processing error: {str(e)}")
                self.delivery_context.discard(event)
        else:
            # Собствено съобщение (ехо през fanout) — ЗАДЪЛЖИТЕЛНО се
            # settle-ва, иначе брокерът го redeliver-ва вечно и опашката
            # се превръща в отровен цикъл от стари heartbeat-и.
            self.delivery_context.accept(event)

    def _forward(self, message: Any) -> None:
        """
        Invokes the optional ``on_message`` forwarder for an accepted message.

        The message body is normalized to a plain ``dict`` (transparently gzip-
        decompressed and JSON-decoded when needed) and passed together with a
        plain ``dict`` copy of the AMQP properties. Forwarder errors propagate to
        :meth:`on_amqp_message` so a failed forward discards the message rather
        than silently accepting it.

        Args:
            message: The received AMQP message (with ``body`` and ``properties``).
        """
        if self._on_message is None:
            return
        payload = self._coerce_payload(message.body)
        properties = message_properties(message)
        self._on_message(payload, properties)

    @staticmethod
    def _coerce_payload(body: Any) -> Dict[str, Any]:
        """
        Best-effort normalization of an AMQP message body to a CFX ``dict``.

        Handles the transport encodings used on the wire: already-decoded dicts
        pass through; bytes/bytearray/memoryview are gzip-decompressed when
        possible and UTF-8 decoded; JSON strings are parsed. Anything that cannot
        be decoded to a JSON object is wrapped as ``{"raw": <value>}`` so the
        forwarder always receives a ``dict``.

        Args:
            body: The raw AMQP message body.

        Returns:
            Dict[str, Any]: The normalized CFX payload.
        """
        if isinstance(body, dict):
            return body
        raw: Any = body
        if isinstance(body, (bytes, bytearray, memoryview)):
            data = bytes(body)
            try:
                data = gzip.decompress(data)
            except (OSError, gzip.BadGzipFile):
                # Не е gzip — ползваме суровите байтове.
                pass
            raw = data.decode("utf-8", errors="replace")
        if isinstance(raw, str):
            try:
                decoded = json.loads(raw)
            except (ValueError, TypeError):
                return {"raw": raw}
            return decoded if isinstance(decoded, dict) else {"data": decoded}
        return {"raw": str(raw)}

    def on_start(self, event: Event) -> None:
        _logger.info(f"The handler is started with client id: {self._client_id}")

    def on_connection_closed(self, event: Event) -> None:
        _logger.info("The connection is closed")

    def on_link_closed(self, event: Event) -> None:
        _logger.info("The link is closed")

    def set_client_id(self, client_id: str) -> None:
        """
        Sets the client ID for the instance.

        This method is used to configure or modify the client ID attribute of the
        instance. The client ID is expected to be provided as a string.

        Args:
            client_id: The new client ID to be set, provided as a string.

        Returns:
            None
        """
        self._client_id = client_id

    def get_client_id(self) -> str:
        """
        Retrieves the client ID associated with the current instance.

        This method returns the unique identifier assigned to the client.
        The client ID is stored as a private attribute of the instance.

        Returns:
            str: The client ID associated with the current instance.
        """
        return self._client_id

    def get_processed(self) -> Any:
        """
        Retrieves the processed data.

        This method provides access to the processed data stored within the
        object. It is intended to retrieve any post-processed information
        that has been previously computed and saved in a private attribute.

        Returns:
            Any: The processed data associated with the object.
        """
        return self._processed

    def get_published(self) -> Any:
        """
        Retrieves the value of the private attribute `_published`.

        This method returns the stored value of `_published`. It does not perform
        any additional computation or validation on the value.

        Returns:
            Any: The value of the `_published` attribute.
        """
        return self._published

    @property
    def client_id(self) -> str:
        """
        Retrieves the client ID associated with this object.

        This property provides access to the private attribute `_client_id`
        and represents the unique identifier for a client within the context
        of the application. It is a read-only property.

        Returns
        -------
        str
            The client ID as a string.
        """
        return self._client_id
