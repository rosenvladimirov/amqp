import argparse
import signal
import sys
import logging
from typing import Optional, Dict
from dataclasses import dataclass
from pathlib import Path
from configparser import ConfigParser

from tools.exeption import ConfigurationError
from transport.amqpendpoint import AmqpEndpoint

# Constants
DEFAULT_EXCHANGE = "CFXExchange"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
_logger = logging.getLogger(__name__)


class ConfigurationManager:
    """
    Manage application configuration by reading and validating INI files.

    This class is responsible for loading, validating, and managing configuration
    settings from INI files. It ensures that required sections are present and
    provides access to configuration data as a dictionary structure.
    """

    def __init__(self):
        self.config = ConfigParser()

    def _validate_sections(self, required_sections: list[str]) -> None:
        """Check if all required sections are present"""
        missing_sections = [section for section in required_sections
                            if not self.config.has_section(section)]
        if missing_sections:
            raise ConfigurationError(
                f"Missing required sections: {', '.join(missing_sections)}"
            )

    def load_config(self, config_path: str) -> Dict[str, Dict[str, str]]:
        """Load configuration from INI file"""
        config_file = Path(config_path)

        try:
            if not config_file.exists():
                raise FileNotFoundError(
                    f"Configuration file does not exist: {config_path}"
                )

            with config_file.open('r', encoding="utf-8") as config_handle:
                self.config.read_file(config_handle)

            self._validate_sections(['connection'])

            return {
                section: dict(self.config.items(section))
                for section in self.config.sections()
            }

        except FileNotFoundError as e:
            _logger.error(f"File not found: {e}")
            raise ConfigurationError(f"Error accessing configuration file: {e}")
        except ConfigurationError as e:
            _logger.error(str(e))
            raise
        except Exception as e:
            _logger.error(f"Unexpected error reading configuration: {e}")
            raise ConfigurationError(f"Error loading configuration: {e}")


@dataclass
class SslSettings:
    ca_cert: str
    client_cert: str
    client_key: str
    p12_store: str
    p12_password: str


class CFXEndpointManager:
    """
    Manages the configuration and lifecycle of a CFX AMQP endpoint.

    Provides mechanisms to create and manage AMQP endpoints for CFX communication.
    This class handles configurations, SSL setups, argument parsing, and signal handling
    to facilitate the setup and proper shutdown of AMQP endpoints in CFX-oriented applications.
    """
    _amqp_endpoint = None
    _running = False
    _heartbeat = None

    def __init__(self):
        self.config_manager = ConfigurationManager()

    def create_ssl_config(self, ssl_settings: Dict) -> Optional[Dict[str, str]]:
        """Create SSL configuration from settings"""
        if not all(ssl_settings.values()):
            return None

        try:
            return {
                'ca_cert': ssl_settings['ca_cert'],
                'client_cert': ssl_settings['client_cert'],
                'client_key': ssl_settings['client_key'],
                'client_p12_store': ssl_settings['p12_store'],
                'client_p12_password': ssl_settings['p12_password']
            }
        except KeyError as e:
            _logger.error(f"Missing SSL setting: {e}")
            return None
        except Exception as e:
            _logger.error(f"Error creating SSL configuration: {e}")
            return None

    def load_config(self, config_path: str) -> Dict[str, Dict[str, str]]:
        """Load configuration using ConfigurationManager"""
        return self.config_manager.load_config(config_path)

    def setup_endpoint(self, args: argparse.Namespace, config: Dict) -> AmqpEndpoint:
        """Create and configure AmqpCFXEndpoint instance"""
        ssl_config = self.create_ssl_config(config.get('ssl', {})) if 'ssl' in config else None
        connection_config = config.get('connection', {})

        endpoint_config = {
            'uri': args.uri or connection_config.get('uri'),
            'queue_name': args.queue or connection_config.get('queue', None),
            'exchange_name': args.exchange or connection_config.get('exchange', DEFAULT_EXCHANGE),
            'routing_key': args.routing_key or connection_config.get('routing_key', None)
        }

        if ssl_config:
            endpoint_config.update(ssl_config)

        return AmqpEndpoint(**endpoint_config)

    @staticmethod
    def parse_arguments() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description='CFX AMQP Endpoint')
        parser.add_argument('--uri',
                            help='AMQP server URI (example: amqp://localhost:5672)')
        parser.add_argument('--queue',
                            help='Message queue name')
        parser.add_argument('--exchange',
                            help=f'Exchange name (default: {DEFAULT_EXCHANGE})')
        parser.add_argument('--routing-key',
                            help='Message routing key')
        parser.add_argument('--config', default='conf/amqp.ini',
                            help='Path to INI config file (default: conf/amqp.ini)')
        return parser.parse_args()

    def run(self):
        args = self.parse_arguments()
        endpoint = None
        config = self.load_config(args.config)
        config.update({
            'uri': args.uri or config.get('connection', {}).get('uri') or '',
            'queue': args.queue or config.get('connection', {}).get('queue') or '',
            'exchange': args.exchange or config.get('connection', {}).get('exchange') or DEFAULT_EXCHANGE,
            'routing_key': args.routing_key or config.get('connection', {}).get('routing_key') or ''
        })


        self._amqp_endpoint = self.setup_endpoint(args, config)

        _logger.info(f"Starting CFX endpoint at {self._amqp_endpoint.uri}")
        _logger.info(f"Listening on queue: {self._amqp_endpoint.queue_name}")
        _logger.info(f"Exchange: {self._amqp_endpoint.exchange_name}")

        if self._amqp_endpoint.routing_key:
            _logger.info(f"Routing key: {self._amqp_endpoint.routing_key}")

        self._running = True
        self._setup_signal_handlers()

        try:
            self._amqp_endpoint.connect()
            while self._running:
                signal.pause()
        except KeyboardInterrupt:
            _logger.info("Termination")
        except Exception as e:
            _logger.error(f"An error occurred: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        _logger.info("Stopping the app...")
        self._running = False

        try:
            self._amqp_endpoint.disconnect()
            # self._heartbeat.disconnect()
        except Exception as e:
            _logger.error(f"Error stopping the AMQP connection: {e}")

        _logger.info("The app is suspended")
        sys.exit(0)

    def _setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        _logger.info(f"Signal: {signal.Signals(signum).name}")
        self.shutdown()


def main():
    manager = CFXEndpointManager()
    manager.run()


if __name__ == '__main__':
    main()
    sys.exit(0)
