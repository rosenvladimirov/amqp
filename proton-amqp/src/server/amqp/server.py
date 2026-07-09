import json
import logging
import socket
import threading
import time
from datetime import datetime
from types import SimpleNamespace
from typing import Optional, Dict, Callable
from dataclasses import dataclass
from urllib.parse import urlparse

from proton import Delivery
from rabbitmq_amqp_python_client import (
    AddressHelper, Environment, Connection,
    Message, PosixSslConfigurationContext, Publisher, Consumer,
    RecoveryConfiguration,
)

from .on_amqp_message import MessageHandler
from .message_processor import MessageProcessor

_logger = logging.getLogger(__name__)


@dataclass
class MessageQueueItem:
    """
    Represents an item in a message queue.

    Holds a message and its associated properties, typically used for messaging
    systems or intermediate data storage.
    """
    message: str
    properties: Dict[str, str]


@dataclass
class SslConfig:
    """Represents the SSL configuration for a secure connection.

    This class is used to encapsulate all the necessary SSL-related
    configuration required to establish a secure connection. It includes
    details about certificates, keys, and password-protected stores. The
    class simplifies the management of SSL configurations by consolidating
    the required elements into a single, structured format.

    Attributes:
        context: PosixSslConfigurationContext
            The SSL configuration context used for establishing connections.
        ca_cert: str
            Path to the certificate authority (CA) certificate file.
        client_cert: str
            Path to the client's certificate file.
        client_key: str
            Path to the client's private key file.
        client_p12_store: str
            Path to the client's PKCS#12 key store file.
        client_p12_password: str
            Password for the client's PKCS#12 key store.
    """
    context: PosixSslConfigurationContext
    ca_cert: str
    client_cert: str
    client_key: str
    client_p12_store: str
    client_p12_password: str


class ConnectionState:
    """
    Manages the connection state in a thread-safe manner.

    This class provides functionality to track and update the connection status
    of a resource while ensuring thread safety through the use of locks. It
    also includes a mechanism to enforce an active connection state by raising
    an error if the connection is inactive.

    Attributes:
        _is_connected (bool): Internal flag indicating whether the connection
            is active or not. Managed in a thread-safe manner.
        _lock (threading.Lock): A lock used to ensure thread-safe access and
            modification of the connection state.
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
            raise ConnectionError("Няма активна връзка с AMQP сървъра")

class MessageQueue:
    """
    Manages a thread-safe queue for message handling.

    This class provides methods to add messages with associated properties to
    a queue, remove messages from the queue, and check if the queue contains
    any messages. Thread-safety is ensured for concurrent interactions.

    Attributes:
        _queue (list[MessageQueueItem]): Internal storage for messages.
        _lock (threading.Lock): Lock to ensure thread-safe operations on
                                the message queue.
    """
    def __init__(self):
        self._queue: list[MessageQueueItem] = []
        self._lock = threading.Lock()

    def push(self, message: str, properties: Dict[str, str]) -> None:
        with self._lock:
            self._queue.append(MessageQueueItem(message, properties))

    def pop(self) -> Optional[MessageQueueItem]:
        with self._lock:
            return self._queue.pop(0) if self._queue else None

    def has_messages(self) -> bool:
        return len(self._queue) > 0

@dataclass
class ConnectionManager:
    """
    Manages the lifecycle of a connection to a messaging environment.

    This class is responsible for initializing, configuring, and maintaining a
    connection to a messaging system. It encapsulates the setup of the environment,
    addresses, and the publisher, handling optional SSL configuration and a
    specific routing key as part of its setup. It also includes functionality
    to gracefully close the connection and release resources upon termination.

    Attributes:
        uri (str): The URI used to establish the connection.
        exchange_name (str): The name of the exchange to interact with.
        queue_name (str): The name of the queue to interact with.
        routing_key (Optional[str]): The routing key used for message filtering
            within the exchange.
        ssl_config (Optional[SslConfig]): SSL configuration for secure connections.
        timeout (Optional[int]): Connection timeout in seconds.
        publisher (Optional[Publisher]): The messaging publisher interface.
        connection (Optional[Connection]): The active connection object.
        exchange_addr (Optional[str]): The exchange address within the environment.
        queue_addr (Optional[str]): The queue address within the environment.
        environment (Optional[Environment]): The environment instance for
            connection setup and management.
    """
    uri: str
    exchange_name: str
    queue_name: str
    routing_key: Optional[str] = None
    ssl_config: Optional[SslConfig] = None
    timeout: Optional[int] = None

    publisher: Optional[Publisher] = None
    connection: Optional[Connection] = None
    exchange_addr: Optional[str] = None
    queue_addr: Optional[str] = None
    environment: Optional[Environment] = None

    def __post_init__(self):
        """
        Initializes post-construction configuration and connections for the instance.

        The method performs critical setup actions after the object is created,
        including validating required attributes, initializing the environment,
        configuring addresses, and setting up the publisher. It raises appropriate
        exceptions if a failure occurs at any step.

        Raises:
            ValueError: If any of the mandatory attributes `uri`, `exchange_name`, or
            `queue_name` is not provided.
            ConnectionError: If there is a failure in resolving the hostname from
            the provided URI or any other connection initialization error.
        """
        if not self.uri or not self.exchange_name or not self.queue_name:
            raise ValueError("URI, exchange_name и queue_name са задължителни")

        try:
            self.environment = self._initialize_environment()
            self.connection = self._create_connection()
            self.exchange_addr, self.queue_addr = self._configure_addresses()
            self.publisher = self.connection.publisher(self.exchange_addr)
        except socket.gaierror:
            parsed = urlparse(self.uri)
            raise ConnectionError(f"Не може да се резолвне хост името: {parsed.hostname}")
        except Exception as e:
            raise ConnectionError(f"Грешка при инициализация на връзката: {str(e)}")

    def _initialize_environment(self) -> Environment:
        """
        Initializes and configures the environment based on the current settings.

        This method creates and returns an Environment instance based on the provided
        URI and SSL configuration. If SSL configuration is supplied, it uses the
        SSL context from the configuration; otherwise, it initializes the Environment
        with just the URI.

        Returns:
            Environment: A configured Environment instance.
        """
        # rabbitmq-amqp-python-client >=0.7 handles reconnection natively via
        # RecoveryConfiguration — the machine/broker link may flap, so keep
        # trying to recover instead of relying on the old manual retry loop.
        recovery = RecoveryConfiguration(active_recovery=True, MaxReconnectAttempts=50)
        if self.ssl_config:
            return Environment(uri=self.uri, ssl_context=self.ssl_config.context,
                               recovery_configuration=recovery)
        return Environment(uri=self.uri, recovery_configuration=recovery)

    def _configure_addresses(self) -> tuple[str, str]:
        """
        Configures and returns the addresses for the exchange and queue.

        This method utilizes the AddressHelper to generate the appropriate
        exchange and queue addresses based on the provided exchange name,
        routing key, and queue name. The resulting addresses are returned
        as a tuple containing the exchange address and the queue address.

        Returns:
            tuple[str, str]: A tuple containing the exchange address and
            queue address.
        """
        exchange = AddressHelper.exchange_address(
            self.exchange_name,
            self.routing_key or ""
        )
        queue = AddressHelper.queue_address(self.queue_name)
        return exchange, queue

    def _create_connection(self) -> Connection:
        """
        Creates and establishes a connection instance for use within the environment.

        This private method initializes a new connection by invoking the appropriate
        environment-specific connection logic and establishes the connection using a
        dial operation.

        Returns:
            Connection: A Connection instance that has been established with the
            environment.
        """
        connection = self.environment.connection()
        connection.dial()
        return connection

    def close(self) -> None:
        """
        Closes the associated environment safely.

        This method checks if the instance has an `environment` attribute and,
        if present, attempts to close the environment safely. Any exceptions
        that occur during this process are logged.

        Exceptions are handled to ensure that the application does not crash
        due to errors when closing the environment.

        Raises:
            Logs an error using `_logger.error` in case of an exception during
            the closing of the environment.

        Returns:
            None
        """
        if hasattr(self, 'environment'):
            try:
                self.environment.close()
            except Exception as e:
                _logger.error(f"Грешка при затваряне на връзката: {str(e)}")


class AmqpServer:
    """
    Represents an AMQP server for managing connections, consuming, and publishing
    messages on an AMQP broker.

    The `AmqpServer` class provides functionality to establish and manage an AMQP
    connection, handle message consumption, and publish messages. It supports
    configuration for connection details, message handlers, SSL settings, timeouts,
    and heartbeat monitoring.

    Attributes:
        DEFAULT_EXCHANGE: Default exchange name used if no specific exchange is
            provided.
        PUBLISHER_TIMEOUT: Timeout for the publisher to wait for new messages before
            proceeding with execution.
        HEARTBEAT_TIMEOUT: Interval time in seconds for sending heartbeat messages.
        CLIENT_ID_PREFIX: Prefix used for generating a unique client ID.
    """

    DEFAULT_EXCHANGE = "CXFExchange"
    PUBLISHER_TIMEOUT = 1
    HEARTBEAT_TIMEOUT = 60
    CLIENT_ID_PREFIX = "proton-amqp-"

    def __init__(
            self,
            uri: str,
            queue_name: str,
            routing_key: Optional[str] = None,
            exchange_name: Optional[str] = None,
            message_handler: Optional[Callable] = None,
            message_heartbeat: Optional[Callable] = None,
            ssl_config: Optional[SslConfig] = None,
            timeout: Optional[int] = 30,
    ) -> None:
        self._thread = None
        self.consumer = None
        self._running = None
        self._validate_input(uri, queue_name)
        self._initialize_core_components()
        self._setup_connection_manager(
            uri, queue_name, routing_key, exchange_name, ssl_config, timeout
        )
        self._setup_message_handling(message_handler)
        self._heartbeat = message_heartbeat

    def _validate_input(self, uri: str, queue_name: str) -> None:
        if not uri or not queue_name:
            raise ValueError("URI and queue name are required")

    def _initialize_core_components(self) -> None:
        self._connection_state = ConnectionState()
        self._message_queue = MessageQueue()
        self._ready = threading.Event()
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._heartbeat: Optional[Callable] = None
        self.consumer: Optional[Consumer] = None

    def _setup_connection_manager(
            self,
            uri: str,
            queue_name: str,
            routing_key: Optional[str],
            exchange_name: Optional[str],
            ssl_config: Optional[SslConfig],
            timeout: Optional[int]
    ) -> None:
        self.connection_manager = ConnectionManager(
            uri=uri,
            exchange_name=exchange_name or self.DEFAULT_EXCHANGE,
            queue_name=queue_name,
            routing_key=routing_key,
            ssl_config=ssl_config,
            timeout=timeout,
        )
        self.publisher = self.connection_manager.publisher

    def _setup_message_handling(self, message_handler: Optional[Callable]) -> None:
        self.client_id = f"{self.CLIENT_ID_PREFIX}{id(self)}"
        self.on_message_handler = message_handler or MessageHandler()
        self.on_message_handler.set_client_id(self.client_id)
        self._connection_state.update_connection_state(True)

    def start_consumer(self) -> None:
        _logger.info("Starting consumer")
        self.consumer = self.connection_manager.connection.consumer(
            self.connection_manager.queue_addr,
            message_handler=self.on_message_handler,
        )

    def start_publisher(self) -> None:
        _logger.info("Starting Publisher")
        self._running = True
        self._thread = threading.Thread(target=self._publisher_loop, daemon=True)
        self._thread.start()
        self._ready.set()

    def _publisher_loop(self) -> None:
        last_heartbeat = time.time()

        while self._running:
            current_time = time.time()
            time_since_heartbeat = current_time - last_heartbeat
            next_heartbeat_in = max(0.0, self.HEARTBEAT_TIMEOUT - time_since_heartbeat)

            wait_timeout = min(self.PUBLISHER_TIMEOUT, next_heartbeat_in)
            got_event = self._ready.wait(timeout=wait_timeout)

            if got_event:
                self._ready.clear()
                self._process_message_queue()

            if time.time() - last_heartbeat >= self.HEARTBEAT_TIMEOUT:
                self._send_heartbeat()
                last_heartbeat = time.time()

    def _send_heartbeat(self) -> None:
        try:
            _logger.debug("Sending Heartbeat")
            if self._heartbeat:
                message, properties = self._heartbeat()
            else:
                message = json.dumps({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat(),
                    "clientId": self.client_id
                })
                properties = {
                    'ClientId': self.client_id,
                    'MessageType': 'Heartbeat',
                    'ContentType': 'application/json'
                }
            self._publish_message(message, properties)
        except Exception as e:
            _logger.error(f"Error Sending Heartbeat: {str(e)}")

    def _process_message_queue(self) -> bool:
        if not self._message_queue.has_messages():
            return False

        message_item = self._message_queue.pop()
        if message_item:
            properties = message_item.properties
            self._publish_message(message_item.message, properties)
        return True

    def _ensure_client_id_in_properties(self, properties: Dict[str, str]) -> None:
        if properties and not properties.get('ClientId'):
            properties['ClientId'] = self.client_id

    def _wait_for_messages(self) -> None:
        self._ready.wait(timeout=self.PUBLISHER_TIMEOUT)
        if self._running:
            self._ready.clear()

    def publish(self, message: str, properties: Dict[str, str]) -> Delivery:
        """
        Publishes a message to the connected server with the given properties.

        The publish method is responsible for sending a message along with its
        associated properties to the server. The method ensures that the
        connection to the server is established before publishing the message.
        It utilizes a thread-safe mechanism by acquiring a lock during the
        process of publishing.

        Arguments:
        message: str
            The content of the message to be published.
        properties: Dict[str, str]
            A dictionary containing key-value pairs representing the properties
            of the message, such as headers or metadata.

        Returns:
        Delivery
            An instance of the Delivery class, indicating the result of the
            publishing operation.
        """
        with self._lock:
            self._connection_state.ensure_connected()
            return self._publish_message(message, properties)

    def _publish_message(self, message: str, properties: Dict[str, str]) -> Delivery:
        try:
            self._ensure_client_id_in_properties(properties)
            processor = MessageProcessor()
            message_dict = {"body": message, "properties": properties}
            message_processed = processor(SimpleNamespace(**message_dict))
            _logger.debug(
                f"Message processed: {message_processed} with properties {properties}"
            )
            # _logger.info(f"Processed {message_processed} with properties {properties}")
            return self.publisher.publish(
                Message(body=message_processed, properties=properties)
            )
        except Exception as e:
            raise RuntimeError(f"Error posting the message: {str(e)}")

    def push_message(self, message: str, properties: Dict[str, str]) -> None:
        self._message_queue.push(message, properties)
        self._ready.set()
