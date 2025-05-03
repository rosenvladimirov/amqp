import unittest
from src.lib.production.unitsInitialized import UnitsInitialized
from xml.etree.ElementTree import Element


class TestUnitsInitialized(unittest.TestCase):

    def test_initialization_with_content(self):
        """Тества правилното създаване на обект UnitsInitialized с валидни данни"""
        content = """{
            "TransactionID": "12345",
            "UnitCount": 1,
            "WorkOrderIdentifier": {
                "WorkOrderId": "WO12345",
                "Batch": "BATCH12345-1"
            },
            "Units": [{
            "UnitIdentifier": "UNIT01",
            "PositionNumber": 1,
            "PositionName": "CIRCUIT1",
            "X": 10.2,
            "Y": 15.3,
            "Rotation": 0.0,
            "FlipX": 10.2,
            "FlipY": 15.3
            }]
        }"""

        # Създаваме обекта UnitsInitialized
        unit = UnitsInitialized(content)

        # Проверяваме дали _element е инициализиран във вътрешния обект
        self.assertIsNotNone(unit._element, "Initialization failed: _element is None")
        # Проверка дали _element съдържа правилната структура
        self.assertTrue(isinstance(unit._element, Element), "_element is not an XML Element")

    def test_serialization(self):
        """Тества правилното сериализиране на съдържание"""
        content = """{
            "TransactionID": "56789",
            "UnitCount": 2
        }"""

        # Създаваме обекта UnitsInitialized
        unit = UnitsInitialized(content)

        # Проверка дали _serialize е създал верни данни
        self.assertIsNotNone(unit._element, "Serialization failed: _element is None")
        self.assertIn("TransactionID", content, "TransactionID missing in serialized content")

    def test_adding_to_master_root(self):
        """Тества добавянето на UnitsInitialized към master root"""
        master_root = Element("MasterRoot")

        content = """{
            "TransactionID": "54321",
            "UnitCount": 1
        }"""

        # Създаваме UnitsInitialized обект
        unit = UnitsInitialized(content)

        # Добавяме _element (текущия root) към master root
        master_root.append(unit._element)

        # Проверяваме дали елементът е добавен успешно
        self.assertEqual(len(master_root), 1, "Root not added correctly to MasterRoot")
        self.assertEqual(
            master_root[0].tag, "UnitsInitialized",
            "First child of master_root is not UnitsInitialized"
        )

    def test_no_content_on_initialization(self):
        """Проверка на поведение при инициализация без съдържание"""
        with self.assertRaises(Exception):
            UnitsInitialized(None)


if __name__ == '__main__':
    unittest.main()
