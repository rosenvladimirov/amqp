# Copyright 2024-2026 Rosen Vladimirov / Terraros Commerce Ltd.
# SPDX-License-Identifier: LGPL-3.0-or-later
# Sent by a process endpoint when the work-stage for a unit or group of units starts
#
# Example JSON format:
# {
#     "TransactionID": "2c24590d-39c5-4039-96a5-91900cecedfa",
#     "Stage": {
#         "StageSequence": 1,
#         "StageName": "STAGE1",
#         "StageType": "Work"
#     }
# }

from typing import Optional
from lib.cfx.cfx_message import CFXMessage


class WorkStageStarted(CFXMessage):
    """
    Represents a message indicating the start of a work stage.

    Provides functionality to initialize with a specific content, process it, and store it
    in a serialized format for further use.
    """
    MESSAGE_TYPE = "WorkStageStarted"

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
