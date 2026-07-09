# CFX information-system work-order management messages.
#
# Sent by an information system (MES / planning) to announce work-order
# lifecycle changes to endpoints on the CFX network. All messages carry a list
# of work orders (or work-order identifiers) in their payload; the concrete
# field set follows the CFX 1.7 specification and is parsed generically from the
# JSON body by the typed CFXMessage machinery.

from typing import Optional
from lib.cfx.cfx_message import CFXMessage


class WorkOrdersCreated(CFXMessage):
    """
    Represents a WorkOrdersCreated message, which inherits from CFXMessage.

    Sent when one or more new work orders have been created in the information
    system. The payload carries the created work orders (identity, product,
    quantity, routing, …). Content is serialized and appended to the message
    root following the standard typed-message pattern.
    """
    MESSAGE_TYPE = "WorkOrdersCreated"

    def __init__(self, content: Optional[str] = None) -> None:
        super().__init__()
        self._content: Optional[str] = content
        self._root.append(self.serialize(content, root_name=self.MESSAGE_TYPE))


class WorkOrdersUpdated(CFXMessage):
    """
    Represents a WorkOrdersUpdated message, which inherits from CFXMessage.

    Sent when one or more existing work orders have been modified. The payload
    carries the updated work orders. Content is serialized and appended to the
    message root following the standard typed-message pattern.
    """
    MESSAGE_TYPE = "WorkOrdersUpdated"

    def __init__(self, content: Optional[str] = None) -> None:
        super().__init__()
        self._content: Optional[str] = content
        self._root.append(self.serialize(content, root_name=self.MESSAGE_TYPE))


class WorkOrdersDeleted(CFXMessage):
    """
    Represents a WorkOrdersDeleted message, which inherits from CFXMessage.

    Sent when one or more work orders have been deleted from the information
    system. The payload carries the identifiers of the deleted work orders.
    Content is serialized and appended to the message root following the
    standard typed-message pattern.
    """
    MESSAGE_TYPE = "WorkOrdersDeleted"

    def __init__(self, content: Optional[str] = None) -> None:
        super().__init__()
        self._content: Optional[str] = content
        self._root.append(self.serialize(content, root_name=self.MESSAGE_TYPE))


class WorkOrderQuantityUpdated(CFXMessage):
    """
    Represents a WorkOrderQuantityUpdated message, which inherits from CFXMessage.

    Sent when the planned quantity of a work order changes. The payload carries
    the affected work-order identifier and its new quantity. Content is
    serialized and appended to the message root following the standard
    typed-message pattern.
    """
    MESSAGE_TYPE = "WorkOrderQuantityUpdated"

    def __init__(self, content: Optional[str] = None) -> None:
        super().__init__()
        self._content: Optional[str] = content
        self._root.append(self.serialize(content, root_name=self.MESSAGE_TYPE))


class WorkOrderStatusUpdated(CFXMessage):
    """
    Represents a WorkOrderStatusUpdated message, which inherits from CFXMessage.

    Sent when the status of a work order changes (e.g. released, on hold,
    completed). The payload carries the affected work-order identifier and its
    new status. Content is serialized and appended to the message root following
    the standard typed-message pattern.
    """
    MESSAGE_TYPE = "WorkOrderStatusUpdated"

    def __init__(self, content: Optional[str] = None) -> None:
        super().__init__()
        self._content: Optional[str] = content
        self._root.append(self.serialize(content, root_name=self.MESSAGE_TYPE))
