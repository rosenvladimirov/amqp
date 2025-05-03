# Sent by a process endpoint to indicate that a stage has been completed.
#
# Example JSON format:
# {
#     "TransactionID": "2c24590d-39c5-4039-96a5-91900cecedfa",
#     "Stage": {
#         "StageSequence": 1,
#         "StageName": "STAGE1",
#         "StageType": "Work"
#     },
#     "Result": "Completed",
#     "PerformanceImpacts": [
#         {
#             "Cause": "LowFeederSpeed"
#         },
#         {
#             "Cause": "AlternativeTrackUsed"
#         }
#     ]
# }

from typing import Optional
from lib.cfx.cfx_message import CFXMessage


class WorkStageCompleted(CFXMessage):
    """
    Represents a specific type of CFXMessage called LogEntryRecorded.

    The class is designed to handle the creation and serialization of a log entry
    message within an XML format. The primary purpose of this class is to provide
    a way to represent log entries as structured messages that can be sent or
    stored in a standardized format.

    Attributes:
    content: Optional[str]
        The content of the message. It defaults to None.
    root: etree.Element
        The root XML element where the serialized content will be appended.

    """
    MESSAGE_TYPE = "WorkStageCompleted"

    def __init__(self, content: Optional[str] = None) -> None:
        """
        Represents initialization and serialization of a message content with a root node.

        Attributes:
        content: Optional[str]
            The content of the message. It defaults to None.

        root: etree.Element
            The root XML element where the serialized content will be appended.

        Parameters:
        content: Optional[str]
            The content of the message to be serialized. Defaults to None.

        """
        super().__init__()
        self._content: Optional[str] = content
        self._root.append(self.serialize(content, root_name=self.MESSAGE_TYPE))
