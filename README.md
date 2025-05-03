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
- Python 3.9 or newer version
- Installed packages:
  - rabbitmq-amqp-python-client

## Installation

bash
# Create virtual environment
conda create -n cfx-env python=3.9
# Activate environment
conda activate cfx-env
# Install dependencies
conda install --file requirements.txt

## Usage
> **Note**: API may change in future versions
