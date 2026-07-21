# Copyright 2024-2026 Rosen Vladimirov / Terraros Commerce Ltd.
# SPDX-License-Identifier: LGPL-3.0-or-later
import xml.etree.ElementTree as ET

from datetime import datetime
from typing import Optional
from lib.cfx.cfx_message import CFXMessage


class WorkCompleted(CFXMessage):
    """
    Represents a specialized message type indicating the completion of work.

    This class extends the CFXMessage class, and is particularly designed to handle
    the "WorkCompleted" type of message within the system. It allows initializing
    the object with optional content, and maintains it in a serialized structure.
    It is used for communication or signaling purposes in workflows or systems.

    Attributes:
        MESSAGE_TYPE (str): A constant that defines the type of message this class represents.

    Methods are inherited from the parent class and are specific to handling and
    processing the serialized message corresponding to "WorkCompleted".
    """
    MESSAGE_TYPE = "WorkCompleted"

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
