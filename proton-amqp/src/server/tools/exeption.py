class AmqpError(Exception):
    """Base exception for AMQP CFX-related errors.

    This is the parent class for all custom exceptions related to AMQP CFX operations.
    It provides a foundation for more specific error types in the AMQP CFX context.
    """

    def __init__(self, message: str = None) -> None:
        self.message = message or "An AMPQ error occurred"
        super().__init__(self.message)


class PublishError(AmqpError):
    """Exception raised when message publishing operations fail.

    This exception is raised when attempts to publish messages to the AMQP server
    encounter errors, such as connection issues or invalid message format.
    """
    default_message = "Message publishing operation failed"

    def __init__(self, message: str = None) -> None:
        super().__init__(message or self.default_message)


class SubscriptionError(AmqpError):
    """Exception raised when subscription operations fail.

    This exception is raised when attempts to subscribe to AMQP queues or
    process subscribed messages encounter errors.
    """
    default_message = "Subscription operation failed"

    def __init__(self, message: str = None) -> None:
        super().__init__(message or self.default_message)


class ConfigurationError(AmqpError):
    """Specialized error for configuration problems"""
    pass
