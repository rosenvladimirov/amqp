# Copyright 2024-2026 Rosen Vladimirov / Terraros Commerce Ltd.
# SPDX-License-Identifier: LGPL-3.0-or-later
import xml.etree.ElementTree as ET

from datetime import datetime
from typing import Optional
from lib.cfx.cfx_message import CFXMessage


class StationStateChanged(CFXMessage):
    """
    Represents a CFX message specific to a station state change event.

    This class is derived from the CFXMessage base class and is designed to handle
    station state change events within the CFX messaging system. It provides the
    necessary structure and methods to serialize and manage the content associated
    with a station state change. The message type is identified as "StationStateChanged".
    """
    MESSAGE_TYPE = "StationStateChanged"

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
