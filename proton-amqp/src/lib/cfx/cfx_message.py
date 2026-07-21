# Copyright 2024-2026 Rosen Vladimirov / Terraros Commerce Ltd.
# SPDX-License-Identifier: LGPL-3.0-or-later
import uuid
from typing import Optional, Dict, Any, Union
import json
import xmltodict
import xml.etree.ElementTree as ET
from dicttoxml2 import dicttoxml

XMLContent = Union[str, ET.Element]


class CFXMessage:
    """
    Represents a CFX message with capabilities to handle XML and JSON transformations.

    This class provides functionalities for creating, serializing, and deserializing
    a CFX message. It is designed to handle content in both XML and JSON formats,
    allowing for conversions between these formats and providing utility functions
    to get the underlying XML and dictionary representations. The primary purpose
    of this class is to assist with message handling in CFX-compatible systems.
    """
    DEFAULT_ROOT_NAME = "CFX"
    DEFAULT_VERSION = "1.7"

    _unique_id = None
    _content: Optional[str]
    _content_type: str = "application/json"
    _content_dict: Dict[str, Any] = {}
    _root: ET.Element
    _source: str = "CFX"
    _target: str = None

    def __init__(self, content: Optional[str] = None) -> None:
        self._content: Optional[str] = content
        self._root: ET.Element = self._create_root_element(content)

    def _create_root_element(self, content: Optional[str]) -> ET.Element:
        """Create a root XML element from content or create an empty root."""
        return self._convert_to_xml(content) if content else ET.Element(self.DEFAULT_ROOT_NAME)

    def _parse_json_to_xml(self, json_str: str, root_name: str) -> ET.Element:
        """Convert JSON string to XML Element."""
        self._content_dict = json.loads(json_str)
        xml_content = dicttoxml(self._content_dict, custom_root=root_name, attr_type=False)
        return ET.fromstring(xml_content)

    def _convert_to_xml(self, content: Optional[XMLContent], root_name: str = DEFAULT_ROOT_NAME) -> ET.Element:
        """Convert input content to XML Element."""
        if not content:
            return ET.Element(root_name)
        if isinstance(content, ET.Element):
            return content
        if isinstance(content, dict):
            self._content_dict = content
            content = json.dumps(content)
        return self._parse_json_to_xml(content, root_name)

    def get_uuid(self) -> str:
        self._unique_id = str(uuid.uuid4())
        return self._unique_id

    def set_source(self, source: str) -> None:
        self._source = source

    def set_target(self, target: str) -> None:
        self._target = target

    def serialize(self, content: Optional[str] = None, root_name: str = DEFAULT_ROOT_NAME) -> ET.Element:
        """
        Convert content to XML and return a JSON string.
        Args:
            content: Optional JSON string to convert
            root_name: Name of the root XML element
        Returns:
            JSON string representation
        """
        if content:
            self._root = self._convert_to_xml(content, root_name)
        return self._root

    def deserialize(self, xml_string: str = False, xpath: str = False) -> str:
        """Convert an XML message to JSON string."""
        if xml_string:
            return json.dumps(xml_string)
        if xpath:
            xml_string = ET.tostring(self._root.find(xpath)).decode('utf-8')
        else:
            xml_string = ET.tostring(self._root).decode('utf-8')
        return json.dumps(xmltodict.parse(xml_string))

    def get_xml_string(self) -> str:
        """Get XML string representation."""
        return ET.tostring(self._root, encoding='utf-8', method='xml').decode('utf-8')

    @property
    def content(self) -> Optional[str]:
        """Get original content."""
        return self._content

    @property
    def content_dict(self) -> Dict[str, Any]:
        """Get original content."""
        return self._content_dict

    @property
    def root(self) -> ET.Element:
        """Get root XML element."""
        return self._root

    @property
    def source(self) -> str:
        return self._source

    @property
    def target(self) -> str:
        return self._target

    def get_xml(self) -> str:
        """Get XML string representation."""
        return ET.tostring(self._root, encoding='utf-8', method='xml').decode('utf-8')

    def get_root_dict(self) -> Dict[str, Any]:
        """Get dictionary representation of the XML message."""
        return xmltodict.parse(self.get_xml())
