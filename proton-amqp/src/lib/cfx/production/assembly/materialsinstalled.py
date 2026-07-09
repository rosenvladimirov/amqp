# Sent by a process endpoint when one or more materials have been installed onto
# a unit (e.g. component placement by a pick-and-place / SMT machine).
#
# Example JSON format:
# {
#     "TransactionId": "2c24590d-39c5-4039-96a5-91900cecedfa",
#     "InstalledMaterials": [
#         {
#             "UnitIdentifier": "PANEL34543535",
#             "UnitPositionNumber": 1,
#             "InstalledComponents": [
#                 {
#                     "ReferenceDesignator": "R1",
#                     "HeadAndNozzle": {
#                         "HeadId": "HEAD1",
#                         "HeadNozzleNumber": 1
#                     },
#                     "Material": {
#                         "InternalPartNumber": "IPN47788",
#                         "UniqueIdentifier": "MAT4567",
#                         "BatchId": "BATCH887788"
#                     },
#                     "CarrierLocation": {
#                         "LocationIdentifier": "UID384747",
#                         "LocationName": "SLOT47"
#                     },
#                     "ElectricalTest": {
#                         "TestResult": "Passed",
#                         "MeasuredValue": 1000.0,
#                         "ExpectedValue": 1000.0
#                     }
#                 }
#             ]
#         }
#     ]
# }

from typing import Optional
from lib.cfx.cfx_message import CFXMessage


class MaterialsInstalled(CFXMessage):
    """
    Represents a MaterialsInstalled message, which inherits from CFXMessage.

    Sent by a process endpoint when one or more materials have been installed
    onto a unit — typically component placement performed by an SMT / pick-and-
    place machine. The payload carries, per installed unit, the list of installed
    components together with the placement head/nozzle, the consumed material
    (internal part number, unique identifier, batch), the carrier location and
    an optional electrical test result.

    The class takes optional content, processes it and appends the serialized
    result to the message root, following the same pattern as the other typed
    CFX production messages.
    """
    MESSAGE_TYPE = "MaterialsInstalled"

    def __init__(self, content: Optional[str] = None) -> None:
        """
        Initializes a MaterialsInstalled message, serializing the given content.

        Attributes:
            _content (Optional[str]): The string content to be processed. If no
                content is provided, it defaults to None.

        Args:
            content (Optional[str]): Represents the content to initialize the
                object with. If not provided, defaults to None.
        """
        super().__init__()
        self._content: Optional[str] = content
        self._root.append(self.serialize(content, root_name=self.MESSAGE_TYPE))
