# Sent by a process endpoint when the work-cycle for a unit or group of units starts
#
# Example JSON format:
# {
#     "TransactionID": "2c24590d-39c5-4039-96a5-91900cecedfa",
#     "Lane": 1,
#     "UnitCount": 2,
#     "Units": [
#         {
#             "UnitIdentifier": "CARRIER5566",
#             "PositionNumber": 1,
#             "PositionName": "CIRCUIT1",
#             "X": 50.45,
#             "Y": 80.66,
#             "Rotation": 0.0,
#             "FlipX": false,
#             "FlipY": false
#         },
#         {
#             "UnitIdentifier": "CARRIER5566",
#             "PositionNumber": 2,
#             "PositionName": "CIRCUIT2",
#             "X": 70.45,
#             "Y": 80.66,
#             "Rotation": 90.0,
#             "FlipX": false,
#             "FlipY": false
#         }
#     ]
# }

from typing import Optional
from lib.cfx.cfx_message import CFXMessage


class WorkStarted(CFXMessage):
    """
    Represents a WorkStarted message, which inherits from CFXMessage.

    This class serves the purpose of initializing a specific type of message
    indicating that a work process has started. It takes optional content,
    processes it, and appends the serialized result to the message root.
    Useful in contexts where the start of some work must be communicated or logged.
    """
    MESSAGE_TYPE = "WorkStarted"

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
