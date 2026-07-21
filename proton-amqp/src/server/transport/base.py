# Copyright 2024-2026 Rosen Vladimirov / Terraros Commerce Ltd.
# SPDX-License-Identifier: LGPL-3.0-or-later
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

_logger = logging.getLogger(__name__)

# Forwarder callback type shared by every transport implementation:
# (cfx_payload, amqp_properties) -> None
OnMessage = Callable[[Dict[str, Any], Dict[str, Any]], None]


class CfxTransport(ABC):
    """
    Abstract base for a single CFX ingest transport.

    A transport owns exactly one connection to a CFX source and delivers every
    received CFX message to the ``on_message`` forwarder. Concrete
    implementations wrap the two supported wire modes — a RabbitMQ/AMQP broker
    (exchange + queue) and raw AMQP 1.0 peer-to-peer (link source/target) — behind
    the same interface, so a single host (e.g. :class:`CFXPlugin`) can run several
    transports of mixed kinds concurrently.

    Attributes:
        on_message (Optional[OnMessage]): Forwarder invoked for every received
            CFX message with ``(cfx_payload, properties)``.
    """

    def __init__(self, on_message: Optional[OnMessage] = None) -> None:
        self.on_message = on_message

    @abstractmethod
    def connect(self) -> None:
        """Establish the connection and start receiving CFX messages."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """Stop receiving and release all resources held by the transport."""
        raise NotImplementedError

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Whether the transport currently holds an active connection."""
        raise NotImplementedError
