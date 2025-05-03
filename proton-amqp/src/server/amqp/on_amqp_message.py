import json
import logging
from typing import Any

from rabbitmq_amqp_python_client import AMQPMessagingHandler, Event
# I will improve it to add rags of plugs
from .message_processor import MessageProcessor

_logger = logging.getLogger(__name__)


class MessageHandler(AMQPMessagingHandler, MessageProcessor):
    """
    Handles CFX messages received via AMQP protocol.

    This class processes incoming AMQP messages, handles errors during message
    processing, and manages the state of processed data. It provides interfaces for
    retrieving processed data and assigning custom processing functions.
    """
    def __init__(self):
        super().__init__()
        self._processed: Any = None
        self._published: Any = None
        self._client_id: str = ""

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
        _logger.info(f"Message received from client: {event.message.properties}")
        if not event.message.properties.get('ClientId', None) == self._client_id:
            try:
                self._process_message(event.message)
                self.delivery_context.accept(event)
            except json.JSONDecodeError:
                _logger.error("JSON Message Decoding Error")
                self.delivery_context.discard(event)
            except Exception as e:
                _logger.error(f"Message processing error: {str(e)}")
                self.delivery_context.discard(event)

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
