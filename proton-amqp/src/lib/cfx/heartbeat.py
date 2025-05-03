import xml.etree.ElementTree as ET

from datetime import datetime
from typing import Optional
from .cfx_message import CFXMessage


class Heartbeat(CFXMessage):
    """
    Represents a Heartbeat message which is a type of CFXMessage.

    This class is designed to create or deserialize heartbeat messages typically used
    in communication systems. Heartbeat messages ensure that a connection is alive,
    monitor system health, and maintain a communication session. The class
    provides functionality for creating new messages with unique properties or
    deserializing an existing one from a JSON string.

    Attributes:
        MESSAGE_TYPE (str): The type identifier for the Heartbeat message.
        MESSAGE_BODY (str): The section name of the message body in the Heartbeat message.
        HEARTBEAT_FREQUENCY (str): The default frequency interval of the Heartbeat message.

    Args:
        content (Optional[str]): Optional JSON string containing the heartbeat message
                                  data. Defaults to None, which creates a new empty
                                  heartbeat message with generated parameters.

    """
    MESSAGE_TYPE = "Heartbeat"
    MESSAGE_BODY = "MessageBody"
    HEARTBEAT_FREQUENCY = "00:01:00"

    def __init__(self, content: Optional[str] = None) -> None:
        """
        Initialize a Heartbeat message.
        Args:
            content: Optional JSON string containing heartbeat message data.
                    If not provided, create an empty heartbeat message.
        """
        super().__init__()
        if not content:
            message_header = ET.Element(self.MESSAGE_TYPE)

            element = ET.Element("MessageName")
            element.text = f'{CFXMessage.DEFAULT_ROOT_NAME}.{self.MESSAGE_TYPE}'
            message_header.append(element)

            element = ET.Element("Version")
            element.text = f'{CFXMessage.DEFAULT_VERSION}'
            message_header.append(element)

            element = ET.Element("timestamp")
            element.text = datetime.now().isoformat()
            message_header.append(element)

            element = ET.Element("UniqueID")
            element.text = self.get_uuid()
            message_header.append(element)

            element = ET.Element("Source")
            element.text = self.source
            message_header.append(element)

            element = ET.Element("Target")
            element.text = self.target
            message_header.append(element)

            element = ET.Element("HeartbeatFrequency")
            element.text = self.HEARTBEAT_FREQUENCY
            message_header.append(element)

            message_body = ET.Element(self.MESSAGE_BODY)
            element = ET.Element("key", {"name": "$type"})
            element.text = f"{CFXMessage.DEFAULT_ROOT_NAME}.{self.MESSAGE_TYPE}"
            message_body.append(element)
            message_header.append(element)

            self._root.append(message_header)
            self._content = self.deserialize()
        else:
            self._content: Optional[str] = content
            self._root.append(self.serialize(content, root_name=self.MESSAGE_TYPE))
