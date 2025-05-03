# <summary>
# Sent when one or more production units are first introduced into the production process flow.
# Unit initialization most often occurs when new production units are first labeled
# with unique identifiers ( or laser marked)
# < code language = "none" >
# {
#     "TransactionID": None,
#     "UnitCount": 2,
#     "WorkOrderIdentifier": {
#         "WorkOrderId": "WO45648798",
#         "Batch": "BATCH45648798-1",
#     },
#     "Units": [{
#         "UnitIdentifier": "UNIT5566687",
#         "PositionNumber": 1,
#         "PositionName": "CIRCUIT1",
#         "X": 50.45,
#         "Y": 80.66,
#         "Rotation": 0.0,
#         "FlipX": False,
#         "FlipY": False,
#     },
#         {
#             "UnitIdentifier": "UNIT5566688",
#             "PositionNumber": 2,
#             "PositionName": "CIRCUIT2",
#             "X": 50.45,
#             "Y": 80.66,
#             "Rotation": 90.0,
#             "FlipX": False,
#             "FlipY": False,
#         }]
# }
# </code>
# </summary>
from lib.cfx.production.cfxmessage import CFXMessage


class UnitsInitialized(CFXMessage):
    _element = None

    def __init__(self, content=None):
        super().__init__()
        if content is None:
            raise Exception("content cannot be None")
        self._element = self.serialize(content=content, root_name="UnitsInitialized")
        self._root.append(self._element)
