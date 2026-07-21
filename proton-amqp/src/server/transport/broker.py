# Copyright 2024-2026 Rosen Vladimirov / Terraros Commerce Ltd.
# SPDX-License-Identifier: LGPL-3.0-or-later
import logging
from typing import Optional

from server.amqp.server import SslConfig
from server.transport.amqpendpoint import AmqpEndpoint
from server.transport.base import CfxTransport, OnMessage

_logger = logging.getLogger(__name__)


class BrokerTransport(CfxTransport):
    """
    CFX transport over a RabbitMQ / AMQP 1.0 broker (exchange + queue).

    Thin adapter over the existing :class:`AmqpEndpoint`, exposing the uniform
    :class:`CfxTransport` interface. This is the current, production transport;
    it is kept behavior-preserving — all broker semantics (recovery, heartbeat,
    publisher) live in :class:`AmqpEndpoint` / :class:`AmqpServer`.

    Attributes:
        endpoint (AmqpEndpoint): The wrapped broker endpoint.
    """

    def __init__(
            self,
            uri: str,
            queue_name: str,
            routing_key: Optional[str] = None,
            exchange_name: Optional[str] = None,
            ssl_config: Optional[SslConfig] = None,
            on_message: Optional[OnMessage] = None,
    ) -> None:
        super().__init__(on_message=on_message)
        self.endpoint = AmqpEndpoint(
            uri=uri,
            queue_name=queue_name,
            routing_key=routing_key,
            exchange_name=exchange_name,
            ssl_config=ssl_config,
            on_message=on_message,
        )

    def connect(self) -> None:
        self.endpoint.connect()

    def disconnect(self) -> None:
        self.endpoint.disconnect()

    @property
    def is_connected(self) -> bool:
        return self.endpoint.is_connected
