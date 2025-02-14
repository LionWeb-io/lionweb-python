import unittest

from serialization.my_node_with_structured_data_type import \
    MyNodeWithStructuredDataType

from lionwebpython.model.impl.dynamic_structured_datype_instance import \
    DynamicStructuredDataTypeInstance


class TestDynamicStructuredDataTypeInstance(unittest.TestCase):

    def test_check_equality(self):

        sdt1 = DynamicStructuredDataTypeInstance(MyNodeWithStructuredDataType.POINT)
        sdt2 = DynamicStructuredDataTypeInstance(MyNodeWithStructuredDataType.POINT)
        sdt3 = DynamicStructuredDataTypeInstance(MyNodeWithStructuredDataType.ADDRESS)

        # The structuredDataType should matter
        self.assertEqual(sdt1, sdt2)
        self.assertNotEqual(sdt1, sdt3)
        self.assertNotEqual(sdt2, sdt3)

        sdt1.set_field_value("x", 10)
        self.assertNotEqual(sdt1, sdt2)

        sdt2.set_field_value("x", 10)
        self.assertEqual(sdt1, sdt2)


if __name__ == "__main__":
    unittest.main()
