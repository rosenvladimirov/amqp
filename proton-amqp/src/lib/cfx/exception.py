class AmqpCFXError(Exception):
    """Base exception for AMQP CFX-related errors.

    This is the parent class for all custom exceptions related to AMQP CFX operations.
    It provides a foundation for more specific error types in the AMQP CFX context.
    """

    def __init__(self, message: str = None) -> None:
        self.message = message or "An AMQP CFX error occurred"
        super().__init__(self.message)
