import time
import unittest
from concurrent.futures import ThreadPoolExecutor

from lionweb.serialization.data.language_version import LanguageVersion
from lionweb.serialization.data.metapointer import MetaPointer
from lionweb.serialization.data.serialized_property_value import \
    SerializedPropertyValue


class TestSerializedPropertyValue(unittest.TestCase):
    """
    Test suite for SerializedPropertyValue class with focus on interning behavior,
    immutability, and integration with MetaPointer.
    """

    def setUp(self):
        """Clear all caches before each test to ensure isolation."""
        SerializedPropertyValue.clear_cache()
        MetaPointer.clear_cache()
        LanguageVersion.clear_cache()

    def tearDown(self):
        """Clear all caches after each test to prevent interference."""
        SerializedPropertyValue.clear_cache()
        MetaPointer.clear_cache()
        LanguageVersion.clear_cache()

    def test_basic_creation(self):
        """Test basic creation of SerializedPropertyValue instances."""
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "nameProperty")
        spv = SerializedPropertyValue(mp, "John")

        self.assertEqual(mp, spv.meta_pointer)
        self.assertEqual("John", spv.value)
        self.assertEqual(mp, spv.get_meta_pointer())
        self.assertEqual("John", spv.get_value())

    def test_creation_with_none_value(self):
        """Test creation with None value."""
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "optionalProperty")

        spv1 = SerializedPropertyValue(mp, None)
        self.assertEqual(mp, spv1.meta_pointer)
        self.assertIsNone(spv1.value)

        spv2 = SerializedPropertyValue(mp)  # Default None value
        self.assertEqual(mp, spv2.meta_pointer)
        self.assertIsNone(spv2.value)

    def test_factory_method(self):
        """Test the factory method 'of' returns interned instances."""
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "nameProperty")

        spv1 = SerializedPropertyValue.of(mp, "John")
        spv2 = SerializedPropertyValue.of(mp, "John")

        # Should be the same object due to interning
        self.assertIs(spv1, spv2)
        self.assertEqual(spv1, spv2)

    def test_constructor_interning(self):
        """Test that constructor also returns interned instances."""
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "nameProperty")

        spv1 = SerializedPropertyValue(mp, "John")
        spv2 = SerializedPropertyValue(mp, "John")

        # Should be the same object due to interning
        self.assertIs(spv1, spv2)

    def test_mixed_creation_methods(self):
        """Test that constructor and factory method return same interned instances."""
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "nameProperty")

        spv1 = SerializedPropertyValue(mp, "John")
        spv2 = SerializedPropertyValue.of(mp, "John")

        # Should be the same object
        self.assertIs(spv1, spv2)

    def test_different_instances_not_interned(self):
        """Test that different parameter combinations create different instances."""
        lv = LanguageVersion("java", "1.8")
        mp1 = MetaPointer(lv, "nameProperty")
        mp2 = MetaPointer(lv, "ageProperty")

        spv1 = SerializedPropertyValue(mp1, "John")
        spv2 = SerializedPropertyValue(mp1, "Jane")  # Different value
        spv3 = SerializedPropertyValue(mp2, "John")  # Different meta pointer
        spv4 = SerializedPropertyValue(mp1, None)  # None value

        # All should be different objects
        instances = [spv1, spv2, spv3, spv4]
        for i in range(len(instances)):
            for j in range(i + 1, len(instances)):
                self.assertIsNot(instances[i], instances[j])

    def test_metapointer_interning_integration(self):
        """Test that MetaPointer interning works with SerializedPropertyValue interning."""
        lv = LanguageVersion("java", "1.8")
        mp1 = MetaPointer(lv, "nameProperty")
        mp2 = MetaPointer(lv, "nameProperty")  # Same as mp1 due to interning

        # MetaPointers should be the same object
        self.assertIs(mp1, mp2)

        # SerializedPropertyValues using these should also be the same
        spv1 = SerializedPropertyValue(mp1, "John")
        spv2 = SerializedPropertyValue(mp2, "John")

        self.assertIs(spv1, spv2)

    def test_equality(self):
        """Test equality comparison works correctly."""
        lv = LanguageVersion("java", "1.8")
        mp1 = MetaPointer(lv, "nameProperty")
        mp2 = MetaPointer(lv, "nameProperty")  # Same as mp1 due to interning
        mp3 = MetaPointer(lv, "ageProperty")

        spv1 = SerializedPropertyValue(mp1, "John")
        spv2 = SerializedPropertyValue(mp2, "John")  # Should be same as spv1
        spv3 = SerializedPropertyValue(mp1, "Jane")  # Different value
        spv4 = SerializedPropertyValue(mp3, "John")  # Different meta pointer

        # Same parameters should be equal
        self.assertEqual(spv1, spv2)
        self.assertTrue(spv1 == spv2)

        # Different parameters should not be equal
        self.assertNotEqual(spv1, spv3)
        self.assertNotEqual(spv1, spv4)
        self.assertFalse(spv1 == spv3)
        self.assertFalse(spv1 == spv4)

    def test_equality_with_none_values(self):
        """Test equality with None values."""
        lv = LanguageVersion("java", "1.8")
        mp1 = MetaPointer(lv, "nameProperty")
        mp2 = MetaPointer(lv, "ageProperty")

        spv1 = SerializedPropertyValue(mp1, None)
        spv2 = SerializedPropertyValue(mp1, None)
        spv3 = SerializedPropertyValue(mp1, "John")
        spv4 = SerializedPropertyValue(mp2, None)

        self.assertEqual(spv1, spv2)
        self.assertNotEqual(spv1, spv3)
        self.assertNotEqual(spv1, spv4)

    def test_equality_with_different_types(self):
        """Test equality comparison with different types."""
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "nameProperty")
        spv = SerializedPropertyValue(mp, "John")

        self.assertNotEqual(spv, "John")
        self.assertNotEqual(spv, 42)
        self.assertNotEqual(spv, None)
        self.assertNotEqual(spv, {"meta_pointer": mp, "value": "John"})

    def test_hash_consistency(self):
        """Test that hash values are consistent for equal objects."""
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "nameProperty")

        spv1 = SerializedPropertyValue(mp, "John")
        spv2 = SerializedPropertyValue(mp, "John")
        spv3 = SerializedPropertyValue(mp, "Jane")

        # Equal objects should have equal hash codes
        self.assertEqual(hash(spv1), hash(spv2))

        # Different objects should generally have different hash codes
        self.assertNotEqual(hash(spv1), hash(spv3))

    def test_hash_with_none_value(self):
        """Test hash calculation with None value."""
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "nameProperty")

        spv1 = SerializedPropertyValue(mp, None)
        spv2 = SerializedPropertyValue(mp, None)
        spv3 = SerializedPropertyValue(mp, "John")

        # Should be able to calculate hash without error
        hash1 = hash(spv1)
        hash2 = hash(spv2)
        hash3 = hash(spv3)

        # Equal objects should have equal hashes
        self.assertEqual(hash1, hash2)

        # Different objects should have different hashes
        self.assertNotEqual(hash1, hash3)

    def test_immutability(self):
        """Test that instances are immutable after creation."""
        lv = LanguageVersion("java", "1.8")
        mp1 = MetaPointer(lv, "nameProperty")
        mp2 = MetaPointer(lv, "ageProperty")
        spv = SerializedPropertyValue(mp1, "John")

        # Setting properties should raise RuntimeError
        with self.assertRaises(RuntimeError) as context:
            spv.set_meta_pointer(mp2)
        self.assertIn("immutable", str(context.exception))

        with self.assertRaises(RuntimeError) as context:
            spv.set_value("Jane")
        self.assertIn("immutable", str(context.exception))

        # Values should remain unchanged
        self.assertEqual(mp1, spv.meta_pointer)
        self.assertEqual("John", spv.value)

    def test_string_representation(self):
        """Test string representation of SerializedPropertyValue."""
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "nameProperty")

        spv1 = SerializedPropertyValue(mp, "John")
        spv2 = SerializedPropertyValue(mp, None)

        str1 = str(spv1)
        str2 = str(spv2)

        # Should contain the meta pointer and value information
        self.assertIn("nameProperty", str1)
        self.assertIn("John", str1)
        self.assertIn("SerializedPropertyValue", str1)

        self.assertIn("nameProperty", str2)
        self.assertIn("None", str2)
        self.assertIn("SerializedPropertyValue", str2)

    def test_repr_consistency(self):
        """Test that __repr__ returns same as __str__."""
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "nameProperty")
        spv = SerializedPropertyValue(mp, "John")

        self.assertEqual(str(spv), repr(spv))

    def test_cache_management(self):
        """Test cache management methods."""
        # Initially cache should be empty
        self.assertEqual(0, SerializedPropertyValue.cache_size())

        # Create some instances
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "nameProperty")

        spv1 = SerializedPropertyValue(mp, "John")
        self.assertEqual(1, SerializedPropertyValue.cache_size())

        SerializedPropertyValue(mp, "Jane")
        self.assertEqual(2, SerializedPropertyValue.cache_size())

        # Creating duplicate should not increase cache size
        spv3 = SerializedPropertyValue(mp, "John")
        self.assertEqual(2, SerializedPropertyValue.cache_size())
        self.assertIs(spv1, spv3)

        # Clear cache
        SerializedPropertyValue.clear_cache()
        self.assertEqual(0, SerializedPropertyValue.cache_size())

    def test_integration_with_component_interning(self):
        """Test integration with MetaPointer and LanguageVersion interning."""
        # Create multiple SerializedPropertyValues that share MetaPointers
        spv1 = SerializedPropertyValue(
            MetaPointer(LanguageVersion("java", "1.8"), "nameProperty"), "John"
        )
        spv2 = SerializedPropertyValue(
            MetaPointer(LanguageVersion("java", "1.8"), "nameProperty"), "Jane"
        )
        spv3 = SerializedPropertyValue(
            MetaPointer(LanguageVersion("java", "1.8"), "ageProperty"), "25"
        )

        # All should share the same LanguageVersion instance
        self.assertIs(
            spv1.meta_pointer.language_version, spv2.meta_pointer.language_version
        )
        self.assertIs(
            spv2.meta_pointer.language_version, spv3.meta_pointer.language_version
        )

        # spv1 and spv2 should share the same MetaPointer instance
        self.assertIs(spv1.meta_pointer, spv2.meta_pointer)

        # But spv3 should have a different MetaPointer
        self.assertIsNot(spv1.meta_pointer, spv3.meta_pointer)

        # All SerializedPropertyValue instances should be different
        self.assertIsNot(spv1, spv2)
        self.assertIsNot(spv2, spv3)

        # Check cache sizes
        self.assertEqual(1, LanguageVersion.cache_size())
        self.assertEqual(2, MetaPointer.cache_size())
        self.assertEqual(3, SerializedPropertyValue.cache_size())

    def test_thread_safety(self):
        """Test thread safety of the interning mechanism."""
        results = []
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "nameProperty")

        def create_serialized_property_value():
            """Create a SerializedPropertyValue instance in a thread."""
            spv = SerializedPropertyValue(mp, "John")
            results.append(spv)
            time.sleep(0.001)  # Small delay to encourage race conditions

        # Create multiple threads that create the same SerializedPropertyValue
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(create_serialized_property_value) for _ in range(20)
            ]
            # Wait for all threads to complete
            for future in futures:
                future.result()

        # All instances should be the same object
        first_instance = results[0]
        for instance in results[1:]:
            self.assertIs(first_instance, instance)

        # Cache should contain only one instance
        self.assertEqual(1, SerializedPropertyValue.cache_size())

    def test_multiple_instances_thread_safety(self):
        """Test thread safety with multiple different instances."""
        results = {}

        def create_different_property_values(thread_id):
            """Create different SerializedPropertyValue instances in each thread."""
            lv = LanguageVersion("java", "1.8")
            mp1 = MetaPointer(lv, "nameProperty")
            mp2 = MetaPointer(lv, "ageProperty")

            values = [
                SerializedPropertyValue(mp1, "John"),
                SerializedPropertyValue(mp1, "Jane"),
                SerializedPropertyValue(mp2, "25"),
                SerializedPropertyValue(mp1, "John"),  # Duplicate
            ]
            results[thread_id] = values

        # Create multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(create_different_property_values, i) for i in range(5)
            ]
            # Wait for all threads to complete
            for future in futures:
                future.result()

        # Check that same parameters result in same instances across threads
        john_name_instances = []
        jane_name_instances = []
        age_instances = []

        for thread_results in results.values():
            john_name_instances.append(thread_results[0])  # John name
            jane_name_instances.append(thread_results[1])  # Jane name
            age_instances.append(thread_results[2])  # Age
            john_name_instances.append(thread_results[3])  # John name duplicate

        # All John name instances should be the same object
        first_john_name = john_name_instances[0]
        for john_name_instance in john_name_instances[1:]:
            self.assertIs(first_john_name, john_name_instance)

        # All Jane name instances should be the same object
        first_jane_name = jane_name_instances[0]
        for jane_name_instance in jane_name_instances[1:]:
            self.assertIs(first_jane_name, jane_name_instance)

        # All age instances should be the same object
        first_age = age_instances[0]
        for age_instance in age_instances[1:]:
            self.assertIs(first_age, age_instance)

        # Cache should contain exactly 3 instances
        self.assertEqual(3, SerializedPropertyValue.cache_size())

    def test_common_property_value_patterns(self):
        """Test common patterns of property values that benefit from interning."""
        lv = LanguageVersion("java", "1.8")

        # Common boolean properties
        abstract_mp = MetaPointer(lv, "abstract")
        final_mp = MetaPointer(lv, "final")

        # Create multiple boolean property values
        abstract_true_instances = [
            SerializedPropertyValue(abstract_mp, "true") for _ in range(10)
        ]
        abstract_false_instances = [
            SerializedPropertyValue(abstract_mp, "false") for _ in range(10)
        ]
        final_true_instances = [
            SerializedPropertyValue(final_mp, "true") for _ in range(10)
        ]

        # All instances with same parameters should be identical
        for i in range(1, len(abstract_true_instances)):
            self.assertIs(abstract_true_instances[0], abstract_true_instances[i])

        for i in range(1, len(abstract_false_instances)):
            self.assertIs(abstract_false_instances[0], abstract_false_instances[i])

        for i in range(1, len(final_true_instances)):
            self.assertIs(final_true_instances[0], final_true_instances[i])

        # Should have only 3 unique instances in cache
        self.assertEqual(3, SerializedPropertyValue.cache_size())

    def test_performance_with_interning(self):
        """Test that interning provides performance benefits."""
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "nameProperty")

        # Create many instances with same parameters
        instances = [SerializedPropertyValue(mp, "CommonName") for _ in range(1000)]

        # All should be the same object
        first_instance = instances[0]
        for instance in instances[1:]:
            self.assertIs(first_instance, instance)

        # Cache should contain only one SerializedPropertyValue instance
        self.assertEqual(1, SerializedPropertyValue.cache_size())

    def test_edge_cases_with_special_values(self):
        """Test edge cases with special string values."""
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "specialProperty")

        # Test with empty string
        spv1 = SerializedPropertyValue(mp, "")
        spv2 = SerializedPropertyValue(mp, "")
        self.assertIs(spv1, spv2)

        # Test with whitespace
        spv3 = SerializedPropertyValue(mp, "   ")
        spv4 = SerializedPropertyValue(mp, "   ")
        self.assertIs(spv3, spv4)

        # Test with special characters
        spv5 = SerializedPropertyValue(mp, "Hello\nWorld\t!")
        spv6 = SerializedPropertyValue(mp, "Hello\nWorld\t!")
        self.assertIs(spv5, spv6)

        # Test with unicode
        spv7 = SerializedPropertyValue(mp, "Hello 世界 🌍")
        spv8 = SerializedPropertyValue(mp, "Hello 世界 🌍")
        self.assertIs(spv7, spv8)

        # All different values should create different instances
        instances = [spv1, spv3, spv5, spv7]
        for i in range(len(instances)):
            for j in range(i + 1, len(instances)):
                self.assertIsNot(instances[i], instances[j])


if __name__ == "__main__":
    unittest.main()
