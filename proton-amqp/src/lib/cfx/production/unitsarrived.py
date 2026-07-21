# Copyright 2024-2026 Rosen Vladimirov / Terraros Commerce Ltd.
# SPDX-License-Identifier: LGPL-3.0-or-later
import xml.etree.ElementTree as ET

from datetime import datetime
from typing import Optional
from lib.cfx.cfx_message import CFXMessage


class UnitsArrived(CFXMessage):
    """
    Represents a message type indicating that units have arrived.

    This class inherits from `CFXMessage` and provides functionality to process
    and serialize content specific to the 'UnitsArrived' message type. It is used
    to create, store, and manipulate the serialized representation of the message
    content.

    Attributes:
        MESSAGE_TYPE (str): A constant indicating the type of the message, set to 'UnitsArrived'.
    """
    MESSAGE_TYPE = "UnitsArrived"

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
