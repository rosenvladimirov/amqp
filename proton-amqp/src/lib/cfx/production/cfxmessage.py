# Copyright 2024-2026 Rosen Vladimirov / Terraros Commerce Ltd.
# SPDX-License-Identifier: LGPL-3.0-or-later
# <summary>
# Abstract base class for all CFX Messages.Contains no data members.
# Provides for the serialization and deserialization of messages to and from JSON format.
# </summary>

from lib.cfx.cfx_message import CFXMessage as cfxMessage


class CFXMessage(cfxMessage):
    _element = None

    def __init__(self, content=None):
        super().__init__(content=content)
        self._element = self.serialize(content, root_name="Production")
        self._root.append(self._element)
