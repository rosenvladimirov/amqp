# Copyright 2024-2026 Rosen Vladimirov / Terraros Commerce Ltd.
# SPDX-License-Identifier: LGPL-3.0-or-later
# **NOTE: Added in CFX 1.2**
#
# Sent when a non-added value action (out of production) relative to a work order is started,
# aborted or completed by a process endpoint.
#
# Example JSON format:
# {
#     "WorkOrderActionInstanceId": "dec7ca54-efc7-4519-a250-0bc7dbeae1d6",
#     "WorkOrderIdentifier": {
#         "WorkOrderId": "WO1122334455",
#         "Batch": null
#     },
#     "TimeStamp": "2018-08-01T13:46:15.5391201-04:00",
#     "Type": "PreProductionOperations",
#     "State": "Started",
#     "Comments": "Feeders loading"
# }

from typing import Optional
from lib.cfx.cfx_message import CFXMessage


class WorkOrderActionExecuted(CFXMessage):
    """
    Represents the execution of a work order action.

    This class is responsible for handling the execution of actions related to work orders.
    It extends `CFXMessage` and facilitates the initialization and serialization of
    message content into an XML structure by appending it to a root node.

    Attributes:
    content: Optional[str]
        The content of the message. It defaults to None.

    root: etree.Element
        The root XML element where the serialized content will be appended.
    """
    MESSAGE_TYPE = "WorkOrderActionExecuted"

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
