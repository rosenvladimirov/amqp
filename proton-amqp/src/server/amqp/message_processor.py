import logging
from abc import ABC
from typing import Any, Callable

# I will improve it to add rags of plugs
from lib.cfx.cfx_processor import CFXProcessor

_logger = logging.getLogger(__name__)


class MessageProcessor(ABC):
    """
    Represents a message processing framework that allows dynamic processing
    capabilities using modules and processors.

    The `MessageProcessor` class is an abstract base class designed to handle
    processing of messages based on dynamically assigned modules and their
    associated processors. This class enables modular and extendable message
    processing by registering new modules with their processors. It is intended
    to be extended and customized with specific use-cases in mind.

    Attributes:
        _processors (dict[str, Callable[[Any], Any]]): A dictionary holding the
            mapping between modules and their respective processors.
        _processed (Any): Stores the result of the last processed message.
    """
    _processors: dict[str, Callable[[Any], Any]] = {
        'cfx-message', CFXProcessor()
    }
    _processed: Any = None

    def __init__(self, module: str = 'cfx-message', processor: Callable[[Any], Any] = str):
            self.add_module(module, processor)

    def _process_message(self, message, module='cfx-message') -> Any:
        body = message.body
        properties = message.properties
        # _logger.info(f"Properties: {properties}")
        # _logger.info(f"Body: {body if isinstance(body, str) else bytes(body).decode('utf-8')}")
        # _logger.info(f"Module: {module}")
        # Подаваме AMQP свойствата като module_path, за да може CFXProcessor да
        # извлече CFX топика ('cfx-message', напр. 'CFX.WorkStarted') и да
        # използва ТИПИЗИРАНИЯ клас, а не генеричния CFXMessage.
        processor = CFXProcessor()
        self._processed = processor(body, properties)
        return self._processed

    def add_module(self, module: str, processor: Callable[[Any], Any]) -> None:
        if module not in self._processors:
            self._processors[module] = processor

    def __call__(self, message, module='cfx-message') -> Any:
        return self._process_message(message, module)

    @property
    def processed(self) -> Any:
        return self._processed
