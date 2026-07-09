# IPC CFX (Connected Factory Exchange) SDK for Python

> **⚠️ WARNING: This is a version under active development!**  
> This project is in the early development stage and may contain unstable code, incomplete functionality or undergo significant changes. Not recommended for use in production environment.

## Description
This is a Python SDK for IPC Connected Factory Exchange (CFX),
an open standard for communication between manufacturing machines and systems.
The SDK is under development
and aims to provide tools for easy integration of the CFX protocol into your Python applications.

## Current Status
- 🚧 Under active development
- ⚠️ API may change without warning 
- 📌 Some functions may not work as expected
- 🔄 Regular updates and changes

## Planned Features
- AMQP messaging protocol for communication
- CFX message processing
- Asynchronous operations support
- Automatic connection management
- Processing of different message types and data

## Requirements
- **Python >= 3.10** (required by `rabbitmq-amqp-python-client` >= 0.8.0)
- **RabbitMQ 4.x** broker (AMQP 1.0)
- Runtime packages (see `proton-amqp/requirements.txt`):
  - `rabbitmq-amqp-python-client>=0.8.0` — AMQP 1.0 transport (vendors qpid-proton internally)
  - `requests` — HTTP forwarder to Odoo
  - `inflection`, `xmltodict`, `dicttoxml2` — CFX message normalisation / JSON↔XML

> **Note:** `python-qpid-proton`, `pika` and `aio-pika` are **not** runtime
> dependencies. Proton is bundled inside `rabbitmq-amqp-python-client`; the
> `proton`/`pika`/`tornado` code under `src/server/examples/` is legacy demo
> material only and is not used by the server.

## Installation

```bash
# Create virtual environment (Python >= 3.10)
python3 -m venv cfx-env
source cfx-env/bin/activate      # Windows: cfx-env\Scripts\activate
# Install dependencies
pip install -r proton-amqp/requirements.txt
```

## Usage
> **Note**: API may change in future versions
