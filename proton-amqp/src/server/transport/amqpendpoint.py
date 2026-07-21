# Copyright 2024-2026 Rosen Vladimirov / Terraros Commerce Ltd.
# SPDX-License-Identifier: LGPL-3.0-or-later
import json
import logging
import threading
import time
from typing import Optional, Dict, Callable

from server.tools.exeption import PublishError, SubscriptionError
from server.amqp.server import AmqpServer, SslConfig
# I will improve it to add rags of plugs
from lib.cfx.heartbeat import Heartbeat

_logger = logging.getLogger(__name__)

class AmqpConfig:
    """
    Configuration settings for AMQP (Advanced Message Queuing Protocol).

    This class provides constant values used for configuring AMQP communication.
    The attributes include settings for heartbeat messages, default exchange name,
    and connection retry and timeout intervals. They are used to ensure consistent
    handling of AMQP-related operations.
    """
    DEFAULT_EXCHANGE_NAME = "CFXExchange"
    CONNECTION_RETRY_INTERVAL_SECONDS = 5
    CONNECTION_TIMEOUT_SECONDS = 30

class ConnectionState:
    """
    Encapsulates and manages the connection state.

    Represents the current connection state with thread-safe operations, ensuring
    that the connection status is properly handled and synchronized in a
    multithreaded environment.
    """
    def __init__(self) -> None:
        self._is_connected: bool = False
        self._lock = threading.Lock()

    @property
    def is_connected(self) -> bool:
        with self._lock:
            return self._is_connected

    def update_connection_state(self, connected: bool) -> None:
        with self._lock:
            self._is_connected = connected

    def ensure_connected(self) -> None:
        if not self.is_connected:
            raise ConnectionError("There is no active connection to the AMQP server")


def cfx_heartbeat():
    properties = {'cfx-topic': 'CFX', 'cfx-message': 'CFX.Heartbeat', 'cfx-handle': 'Amqp.test.lib', 'cfx-target': None}
    message = Heartbeat().deserialize(xpath=".//Heartbeat")
    # _logger.info(
    #     f"Sending heartbeat message: {message} with properties: {properties}"
    # )
    return message, properties


class AmqpEndpoint:
    """
    Represents an AMQP endpoint for managing connections to an AMQP server, publishing
    messages, and subscribing to a queue.

    This class provides functionality for establishing and maintaining a connection
    to an AMQP server. It allows publishing messages with custom properties to an
    exchange, handling connection errors, and managing the AMQP server's lifecycle.
    The class also ensures proper cleanup of resources upon disconnection.

    Attributes:
        _connection_state (Optional[ConnectionState]): Tracks the state of the
            connection to the AMQP server.
        Amqp_server (Optional[AmqpServer]): Represents the AMQP server, which
            provides methods for publishing and consuming messages.
        _heartbeat_running (Optional[bool]): Indicates whether the heartbeat
            mechanism is running.
    """
    _connection_state: Optional[ConnectionState] = None
    amqp_server: Optional[AmqpServer] = None
    _heartbeat_running: Optional[bool] = None

    def __init__(
            self,
            uri: str,
            queue_name: str,
            routing_key: Optional[str] = None,
            exchange_name: Optional[str] = None,
            ssl_config: Optional[SslConfig] = None,
            on_message: Optional[Callable] = None,
    ) -> None:
        self._connection_state = ConnectionState()
        self.amqp_server = AmqpServer(
            uri=uri,
            queue_name=queue_name,
            routing_key=routing_key,
            exchange_name=exchange_name or AmqpConfig.DEFAULT_EXCHANGE_NAME,
            ssl_config=ssl_config,
            message_heartbeat=cfx_heartbeat,
            on_message=on_message,
        )
        self._connection_state.update_connection_state(True)

    def connect(self) -> None:
        """
        Retries connecting to a server within a specified timeout period.

        This method attempts to establish a connection to the server by running the
        server logic. If the connection fails due to either a `ConnectionError` or
        `SubscriptionError`, the method will retry a configurable number of times.
        Between retries, it waits for a specified interval before attempting again.
        If the connection cannot be established within the timeout period, a
        `ConnectionError` is raised.

        Raises:
            ConnectionError: If the connection attempt fails within the timeout period.
        """
        attempts = 0
        while attempts < AmqpConfig.CONNECTION_TIMEOUT_SECONDS:
            try:
                self._run_server()
                return
            except (ConnectionError, SubscriptionError) as error:
                self._handle_connection_error(error)
                attempts += 1
                time.sleep(AmqpConfig.CONNECTION_RETRY_INTERVAL_SECONDS)
        raise ConnectionError("Failed attempt to connect at the specified time")

    def _run_server(self) -> None:
        self.amqp_server.start_publisher()
        self.amqp_server.start_consumer()

    def _handle_connection_error(self, error: Exception) -> None:
        self._connection_state.update_connection_state(False)
        self._stop_server()
        _logger.error(f"Connection error: {error}")

    def send_message(self, message: str, properties: Dict[str, str]) -> None:
        self._connection_state.ensure_connected()
        try:
            self.amqp_server.publish(message, properties)
        except PublishError as error:
            _logger.error(f"Rehearse when sending a message: {error}")
            raise

    def disconnect(self) -> None:
        try:
            self._cleanup_resources()
        except ConnectionError as error:
            _logger.error(f"Error closing the link: {error}")
        finally:
            self._connection_state.update_connection_state(False)
            _logger.info("The connection is closed")

    def _cleanup_resources(self) -> None:
        self._stop_publisher()
        self._stop_server()

    def _stop_publisher(self) -> None:
        self.amqp_server.connection_manager.publisher.close()
        self._heartbeat_running = False

    def _stop_server(self) -> None:
        # първо спри run() loop-а (иначе close() блокира), после самия link
        stop = getattr(self.amqp_server, "stop_consumer", None)
        if callable(stop):
            stop()
        if self.amqp_server.consumer is not None:
            self.amqp_server.consumer.close()

    @property
    def uri(self) -> str:
        return self.amqp_server.connection_manager.uri

    @property
    def exchange_name(self) -> str:
        return self.amqp_server.connection_manager.exchange_name

    @property
    def queue_name(self) -> str:
        return self.amqp_server.connection_manager.queue_name

    @property
    def routing_key(self) -> Optional[str]:
        return self.amqp_server.connection_manager.routing_key

    @property
    def is_connected(self) -> bool:
        return self._connection_state.is_connected
