import xml.etree.ElementTree as ET

from datetime import datetime
from typing import Optional
from lib.cfx.cfx_message import CFXMessage


class UnitsDeparted(CFXMessage):
    """
    Represents a message indicating that units have departed.

    This class is a specific type of `CFXMessage` with the purpose of handling and processing
    messages that represent the departure of units. It provides functionalities to initialize
    such messages and serialize their content for further use.
    """
    MESSAGE_TYPE = "UnitsDeparted"

    def __init__(self, content: Optional[str] = None) -> None:
        """
        Represents the initialization of an object that processes a given content and stores it in a serialized format.

        Attributes:
            _content (Optional[str]): The string content to be processed. If no content is provided, it defaults to None.

        Args:
            content (Optional[str]): Represents the content to initialize the object with.
                If not provided, defaults to None.
        """
        super().__init__()
        self._content: Optional[str] = content
        self._root.append(self.serialize(content, root_name=self.MESSAGE_TYPE))
