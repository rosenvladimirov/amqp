# Copyright 2024-2026 Rosen Vladimirov / Terraros Commerce Ltd.
# SPDX-License-Identifier: LGPL-3.0-or-later
import xml.etree.ElementTree as ET

from datetime import datetime
from typing import Optional
from lib.cfx.cfx_message import CFXMessage


class LogEntryRecorded(CFXMessage):
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
    MESSAGE_TYPE = "LogEntryRecorded"

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
