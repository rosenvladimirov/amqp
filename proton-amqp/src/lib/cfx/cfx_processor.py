import gzip
import json
import logging
import sys
from typing import Union, Any, Optional, Dict
import importlib
import os
import inflection

from lib.cfx.cfx_message import CFXMessage

# Typical definitions
CFXData = Optional[Union[Dict, str, bytes, bytearray,]]
ProcessedResult = Optional[Union[Dict, Any]]

# System roads
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Logging configuration
_logger = logging.getLogger(__name__)


class CFXProcessor:
    """
    Class responsible for processing data through configurable modules.

    CFXProcessor manages the handling and processing of input data leveraging
    configurable module paths. It supports processing data in multiple formats
    and provides utilities for normalization, camelCase conversion, and
    post-processing hooks.

    Attributes:
        DEFAULT_MODULE_PATH: Default path to the processing module used by the processor.
        CFX_IMPORT_PATH: Hardcoded import path for the main CFX message processing module.
        LIB_PACKAGE_NAME: The package name used for import operations.

    Methods:
        __init__: Initializes the processor with a default or user-defined module path.
        __call__: Enables the class instance to be used as a callable, allowing
                  on-the-fly updates to module paths and data processing.
        process_data: Processes the input data based on its type and returns the
                      processed result.
        post_process_data: Does additional processing after the primary data handling.
        _normalize_module_path: Private utility to normalize the module path for
                                consistent formatting.
        _convert_to_camel_case: Private method to transform a module name to CamelCase.
        _convert_keys_to_uppercase: Private method to convert all dictionary keys to
                                    uppercase.
        _import_module: Dynamically imports a module using provided configurations.
        _process_string_data: Processes the input string data using the predefined
                              module configuration.
        _update_module_config: Updates the module path and internal configuration
                               based on the new path.
    """

    # Configuration constants
    DEFAULT_MODULE_PATH = "cfx.cfx_message"
    DEFAULT_MODULE_NAME = "CFXMessage"
    CFX_IMPORT_PATH = "cfx.cfx_message"
    LIB_PACKAGE_NAME = "cfx"

    def __init__(self, module_path: str = DEFAULT_MODULE_PATH) -> None:
        """
        Initializes an instance of the class that handles module path normalization and
        name conversion operations. The instance stores the normalized module path and
        its camel case name representation upon initialization.

        Attributes:
            _module_path (str): The normalized path of the module.
            _module_name (str): The camel case representation of the module name.

        Parameters:
            module_path: The file path to the module.
        """
        self._module_path = self._normalize_module_path(module_path)
        module_name = self._convert_to_camel_case(module_path)
        if module_name.lower() == self.DEFAULT_MODULE_NAME.lower():
            module_name = self.DEFAULT_MODULE_NAME
        self._module_name = module_name

    def __call__(self, data: CFXData = None, module_path: Optional[str] = None) -> ProcessedResult:
        """
        A callable object for processing data using a specified module path.

        This class method processes the given data based on the optionally provided
        module configuration specified by a file path and then returns the processed
        result.

        Args:
            data: CFXData
                The input data to be processed. Defaults to None if not provided.
            module_path: Optional[str]
                The file path to the module configuration to be used for updating
                the processing configuration. Defaults to None.

        Returns:
            ProcessedResult
                The outcome resulting from processing the provided input data.

        """
        if module_path:
            if isinstance(module_path, dict):
                module_path = module_path.get("cfx-message", self.DEFAULT_MODULE_PATH)
            self._update_module_config(module_path)

        return self.process_data(data)

    def process_data(self, data: CFXData = None) -> ProcessedResult:
        """
        Processes the input data and returns a processed result based on the type of input.
        This function can handle data of type dictionary or string. If the input is a dictionary,
        it converts the keys to uppercase. If the input is a string, it processes the
        string data. For any other data type, it raises a TypeError.

        Parameters:
            data (CFXData, optional): The input data to be processed. Can be of type
            dictionary or string. If not provided, the function returns None.

        Returns:
            ProcessedResult: The result of processing the input data. The specific
            return value depends on the input data type and internal processing logic.

        Raises:
            TypeError: If the input data is neither a dictionary nor a string.
        """
        if data is None:
            return None

        if isinstance(data, dict):
            _logger.info(f"Message: {data}")
            processed_message = json.dumps(self._convert_keys_to_uppercase(data))
            return gzip.compress(processed_message.encode('utf-8'))

        if isinstance(data, memoryview):
            decompressed_data = gzip.decompress(data)
            decode_data = decompressed_data.decode('utf-8')
            _logger.info(f"Message: {decode_data}")
            processed = self._process_string_data(decode_data)
            processed_message = processed.deserialize(processed.content_dict)
            _logger.info(f"Processed Message: {processed.content_dict}")
            return gzip.compress(processed_message.encode('utf-8'))

        if isinstance(data, str):
            _logger.info(f"Message: {data}")
            processed = self._process_string_data(data)
            processed_message = processed.deserialize(processed.content_dict)
            _logger.info(f"Processed Message: {processed.content_dict}")
            return gzip.compress(processed_message.encode('utf-8'))

        raise TypeError("Data must be of type DICT or Str")

    def post_process_data(self, processor: CFXMessage) -> None:
        """
        Processes data using the provided processor.

        This method takes a processor of type CFXMessage and applies
        a post-processing step. It does not return any value and directly
        modifies data as per the processor's operations. The method ensures
        data integrity and prepares it for further consumption.

        Parameters:
        processor: CFXMessage
            The processor instance used to perform post-processing on
            the data.
        """
        pass

    # Помощни методи
    @staticmethod
    def _normalize_module_path(path: str) -> str:
        """
        Converts the module path to a normalized format. This is done by converting
        it to lowercase and replacing 'CXF.' with an empty string.

        Parameters:
            path: str
                The module path that needs to be normalized.

        Returns:
            str
                The normalized version of the module path.
        """
        return path.lower().replace('CXF.', '')

    @staticmethod
    def _convert_to_camel_case(module_path: str) -> str:
        """
        Converts a module path string into its camel case representation.

        This static method takes a module path, extracts the last segment of the path
        (separated by '.'), and converts it into a camel case using the `camelize`
        function from the `inflection` library. It is used for name conversion
        purposes where camel case formatting is required.

        Args:
            module_path (str): The full module path string separated by dots,
            where each dot represents a namespace or module hierarchy.

        Returns:
            str: A string representing the last segment of the module path
            converted to camel case.
        """
        if module_path.split(".")[-1].lower() == CFXProcessor.DEFAULT_MODULE_PATH.lower():
            return CFXProcessor.DEFAULT_MODULE_NAME
        return inflection.camelize(module_path.split(".")[-1])

    @staticmethod
    def _convert_keys_to_uppercase(data: Dict) -> Dict:
        """
        Converts all keys in a dictionary to uppercase.

        This static method takes a dictionary as input and returns a new dictionary
        where all the keys are converted to their uppercase equivalents, while preserving
        the original values associated with each key.

        Args:
            data (Dict): The dictionary whose keys need to be converted to uppercase.

        Returns:
            Dict: A new dictionary with all keys converted to uppercase.
        """
        return {k.upper(): v for k, v in data.items()}

    def _import_module(self, import_path: str) -> Any:
        """
        This method handles the import of a module. It imports the specified module
        using the provided import path. If the import path matches the predefined
        constant `CFX_IMPORT_PATH`, it imports the module directly. Otherwise, it
        imports the module within the namespace of `LIB_PACKAGE_NAME`.

        Args:
            import_path (str): The path of the module to be imported.

        Returns:
            Any: The imported module.
        """
        return (importlib.import_module(import_path) if import_path == self.CFX_IMPORT_PATH
                else importlib.import_module(import_path, self.LIB_PACKAGE_NAME))

    def _process_string_data(self, data: str) -> ProcessedResult:
        """
        Processes string data using a dynamically imported module and
        executes post-processing on the result.

        Attributes:
            _module_path (str): Path to the module to be dynamically imported.
            _module_name (str): Name of the class or processor to be initialized.

        Args:
            data (str): Input string data to be processed.

        Returns:
            ProcessedResult: The result of processing the input data through
            the dynamically imported processor.

        Raises:
            ImportError: If the module specified by _module_path cannot be imported.
            AttributeError: If the attribute specified by _module_name does not
            exist in the imported module.
            Any exceptions are raised by dynamically imported modules or post-processing
            methods during execution.
        """
        processor_module = self._import_module(self._module_path)
        processor = getattr(processor_module, self._module_name)(data)
        self.post_process_data(processor)
        return processor

    def _update_module_config(self, module_path: str) -> None:
        """
        Updates the module configuration by normalizing the provided module path and
        converting it to a camel case format to derive the module name.

        Args:
            module_path (str): The file path of the module to update.

        Returns:
            None
        """
        self._module_path = self._normalize_module_path(module_path)
        self._module_name = self._convert_to_camel_case(module_path)
