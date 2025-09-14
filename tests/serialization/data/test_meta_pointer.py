import time
import unittest
from concurrent.futures import ThreadPoolExecutor

from lionweb.serialization.data.language_version import LanguageVersion
from lionweb.serialization.data.metapointer import MetaPointer


class TestMetaPointer(unittest.TestCase):
    """
    Test suite for MetaPointer class with focus on interning behavior,
    LanguageVersion integration, and thread safety.
    """

    def setUp(self):
        """Clear caches before each test to ensure isolation."""
        MetaPointer.clear_cache()
        LanguageVersion.clear_cache()

    def tearDown(self):
        """Clear caches after each test to prevent interference."""
        MetaPointer.clear_cache()
        LanguageVersion.clear_cache()

    def test_basic_creation(self):
        """Test basic creation of MetaPointer instances."""
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "String")

        self.assertEqual(lv, mp.language_version)
        self.assertEqual("String", mp.key)
        self.assertEqual("java", mp.language)
        self.assertEqual("1.8", mp.version)

    def test_creation_with_none_values(self):
        """Test creation with None values."""
        mp1 = MetaPointer(None, None)
        self.assertIsNone(mp1.language_version)
        self.assertIsNone(mp1.key)
        self.assertIsNone(mp1.language)
        self.assertIsNone(mp1.version)

        lv = LanguageVersion("java", "1.8")
        mp2 = MetaPointer(lv, None)
        self.assertEqual(lv, mp2.language_version)
        self.assertIsNone(mp2.key)

        mp3 = MetaPointer(None, "String")
        self.assertIsNone(mp3.language_version)
        self.assertEqual("String", mp3.key)

    def test_factory_method(self):
        """Test the factory method 'of' returns interned instances."""
        lv = LanguageVersion("java", "1.8")
        mp1 = MetaPointer.of(lv, "String")
        mp2 = MetaPointer.of(lv, "String")

        # Should be the same object due to interning
        self.assertIs(mp1, mp2)
        self.assertEqual(mp1, mp2)

    def test_constructor_interning(self):
        """Test that constructor also returns interned instances."""
        lv = LanguageVersion("java", "1.8")
        mp1 = MetaPointer(lv, "String")
        mp2 = MetaPointer(lv, "String")

        # Should be the same object due to interning
        self.assertIs(mp1, mp2)

    def test_mixed_creation_methods(self):
        """Test that constructor and factory method return same interned instances."""
        lv = LanguageVersion("java", "1.8")
        mp1 = MetaPointer(lv, "String")
        mp2 = MetaPointer.of(lv, "String")

        # Should be the same object
        self.assertIs(mp1, mp2)

    def test_different_instances_not_interned(self):
        """Test that different parameter combinations create different instances."""
        lv1 = LanguageVersion("java", "1.8")
        lv2 = LanguageVersion("kotlin", "1.9")

        mp1 = MetaPointer(lv1, "String")
        mp2 = MetaPointer(lv1, "Integer")
        mp3 = MetaPointer(lv2, "String")
        mp4 = MetaPointer(None, "String")

        # All should be different objects
        instances = [mp1, mp2, mp3, mp4]
        for i in range(len(instances)):
            for j in range(i + 1, len(instances)):
                self.assertIsNot(instances[i], instances[j])

    def test_language_version_interning_integration(self):
        """Test that LanguageVersion interning works with MetaPointer interning."""
        # Create same LanguageVersion instances
        lv1 = LanguageVersion("java", "1.8")
        lv2 = LanguageVersion("java", "1.8")

        # LanguageVersions should be the same object
        self.assertIs(lv1, lv2)

        # MetaPointers using these should also be the same
        mp1 = MetaPointer(lv1, "String")
        mp2 = MetaPointer(lv2, "String")

        self.assertIs(mp1, mp2)

    def test_equality(self):
        """Test equality comparison works correctly."""
        lv1 = LanguageVersion("java", "1.8")
        lv2 = LanguageVersion("java", "1.8")  # Same as lv1 due to interning
        lv3 = LanguageVersion("kotlin", "1.9")

        mp1 = MetaPointer(lv1, "String")
        mp2 = MetaPointer(lv2, "String")  # Should be same as mp1
        mp3 = MetaPointer(lv1, "Integer")  # Different key
        mp4 = MetaPointer(lv3, "String")  # Different language version

        # Same parameters should be equal
        self.assertEqual(mp1, mp2)
        self.assertTrue(mp1 == mp2)

        # Different parameters should not be equal
        self.assertNotEqual(mp1, mp3)
        self.assertNotEqual(mp1, mp4)
        self.assertFalse(mp1 == mp3)
        self.assertFalse(mp1 == mp4)

    def test_equality_with_none(self):
        """Test equality with None values."""
        mp1 = MetaPointer(None, None)
        mp2 = MetaPointer(None, None)
        lv = LanguageVersion("java", "1.8")
        mp3 = MetaPointer(lv, None)
        mp4 = MetaPointer(None, "String")

        self.assertEqual(mp1, mp2)
        self.assertNotEqual(mp1, mp3)
        self.assertNotEqual(mp1, mp4)
        self.assertNotEqual(mp3, mp4)

    def test_equality_with_different_types(self):
        """Test equality comparison with different types."""
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "String")

        self.assertNotEqual(mp, "String")
        self.assertNotEqual(mp, 42)
        self.assertNotEqual(mp, None)
        self.assertNotEqual(mp, {"language_version": lv, "key": "String"})

    def test_hash_consistency(self):
        """Test that hash values are consistent for equal objects."""
        lv = LanguageVersion("java", "1.8")
        mp1 = MetaPointer(lv, "String")
        mp2 = MetaPointer(lv, "String")
        mp3 = MetaPointer(lv, "Integer")

        # Equal objects should have equal hash codes
        self.assertEqual(hash(mp1), hash(mp2))

        # Different objects should generally have different hash codes
        self.assertNotEqual(hash(mp1), hash(mp3))

    def test_hash_with_none(self):
        """Test hash calculation with None values."""
        mp1 = MetaPointer(None, None)
        mp2 = MetaPointer(None, None)
        lv = LanguageVersion("java", "1.8")
        mp3 = MetaPointer(lv, None)

        # Should be able to calculate hash without error
        hash1 = hash(mp1)
        hash2 = hash(mp2)
        hash3 = hash(mp3)

        # Equal objects should have equal hashes
        self.assertEqual(hash1, hash2)

        # Different objects should have different hashes
        self.assertNotEqual(hash1, hash3)

    def test_backward_compatibility_properties(self):
        """Test backward compatibility properties."""
        lv = LanguageVersion("java", "1.8")
        mp = MetaPointer(lv, "String")

        # Test backward compatibility properties
        self.assertEqual("java", mp.language_key)
        self.assertEqual("1.8", mp.language_version_string)

        # Test with None LanguageVersion
        mp_none = MetaPointer(None, "String")
        self.assertIsNone(mp_none.language_key)
        self.assertIsNone(mp_none.language_version_string)

    def test_string_representation(self):
        """Test string representation of MetaPointer."""
        lv = LanguageVersion("java", "1.8")
        mp1 = MetaPointer(lv, "String")
        mp2 = MetaPointer(None, None)

        str1 = str(mp1)
        str2 = str(mp2)

        # Should contain the language version and key information
        self.assertIn("java", str1)
        self.assertIn("1.8", str1)
        self.assertIn("String", str1)
        self.assertIn("MetaPointer", str1)

        self.assertIn("None", str2)
        self.assertIn("MetaPointer", str2)

    def test_cache_management(self):
        """Test cache management methods."""
        # Initially cache should be empty
        self.assertEqual(0, MetaPointer.cache_size())

        # Create some instances
        lv = LanguageVersion("java", "1.8")
        mp1 = MetaPointer(lv, "String")
        self.assertEqual(1, MetaPointer.cache_size())

        MetaPointer(lv, "Integer")
        self.assertEqual(2, MetaPointer.cache_size())

        # Creating duplicate should not increase cache size
        mp3 = MetaPointer(lv, "String")
        self.assertEqual(2, MetaPointer.cache_size())
        self.assertIs(mp1, mp3)

        # Clear cache
        MetaPointer.clear_cache()
        self.assertEqual(0, MetaPointer.cache_size())

    def test_from_language_entity(self):
        """Test creating MetaPointer from language entity."""

        # Create mock language entity
        class MockLanguage:
            def get_key(self):
                return "java"

            def get_version(self):
                return "1.8"

        class MockEntity:
            def __init__(self):
                self.language = MockLanguage()
                self.id = "String"

            def get_key(self):
                return "StringClass"

        entity = MockEntity()
        mp = MetaPointer.from_language_entity(entity)

        self.assertEqual("java", mp.language)
        self.assertEqual("1.8", mp.version)
        self.assertEqual("StringClass", mp.key)

    def test_from_language_entity_with_id_fallback(self):
        """Test creating MetaPointer from entity without get_key method."""

        class MockLanguage:
            def get_key(self):
                return "java"

            def get_version(self):
                return "1.8"

        class MockEntity:
            def __init__(self):
                self.language = MockLanguage()
                self.id = "String"

        entity = MockEntity()
        mp = MetaPointer.from_language_entity(entity)

        self.assertEqual("java", mp.language)
        self.assertEqual("1.8", mp.version)
        self.assertEqual("String", mp.key)  # Falls back to id

    def test_from_language_entity_without_language(self):
        """Test creating MetaPointer from entity without language."""

        class MockEntity:
            def __init__(self):
                self.id = "String"

            def get_key(self):
                return "StringClass"

        entity = MockEntity()
        mp = MetaPointer.from_language_entity(entity)

        self.assertIsNone(mp.language_version)
        self.assertIsNone(mp.language)
        self.assertIsNone(mp.version)
        self.assertEqual("StringClass", mp.key)

    def test_from_keyed(self):
        """Test creating MetaPointer from keyed object and language."""

        class MockLanguage:
            def get_key(self):
                return "java"

            def get_version(self):
                return "1.8"

        class MockKeyed:
            def get_key(self):
                return "StringClass"

        language = MockLanguage()
        keyed = MockKeyed()
        mp = MetaPointer.from_keyed(keyed, language)

        self.assertEqual("java", mp.language)
        self.assertEqual("1.8", mp.version)
        self.assertEqual("StringClass", mp.key)

    def test_from_keyed_with_id_fallback(self):
        """Test creating MetaPointer from keyed object without get_key method."""

        class MockLanguage:
            def get_key(self):
                return "java"

            def get_version(self):
                return "1.8"

        class MockKeyed:
            def __init__(self):
                self.id = "String"

        language = MockLanguage()
        keyed = MockKeyed()
        mp = MetaPointer.from_keyed(keyed, language)

        self.assertEqual("java", mp.language)
        self.assertEqual("1.8", mp.version)
        self.assertEqual("String", mp.key)  # Falls back to id

    def test_from_keyed_without_language(self):
        """Test creating MetaPointer from keyed object without language."""

        class MockKeyed:
            def get_key(self):
                return "StringClass"

        keyed = MockKeyed()
        mp = MetaPointer.from_keyed(keyed, None)

        self.assertIsNone(mp.language_version)
        self.assertEqual("StringClass", mp.key)

    def test_from_feature(self):
        """Test creating MetaPointer from feature."""

        class MockLanguage:
            def get_key(self):
                return "java"

            def get_version(self):
                return "1.8"

        class MockContainer:
            def __init__(self):
                self.language = MockLanguage()

        class MockFeature:
            def __init__(self):
                self._container = MockContainer()

            def get_container(self):
                return self._container

            def get_key(self):
                return "nameProperty"

        feature = MockFeature()
        mp = MetaPointer.from_feature(feature)

        self.assertEqual("java", mp.language)
        self.assertEqual("1.8", mp.version)
        self.assertEqual("nameProperty", mp.key)

    def test_from_feature_without_container(self):
        """Test creating MetaPointer from feature without container."""

        class MockFeature:
            def __init__(self):
                self.id = "nameProperty"

            def get_key(self):
                return "nameProperty"

        feature = MockFeature()
        mp = MetaPointer.from_feature(feature)

        self.assertIsNone(mp.language_version)
        self.assertEqual("nameProperty", mp.key)

    def test_from_feature_with_id_fallback(self):
        """Test creating MetaPointer from feature without get_key method."""

        class MockLanguage:
            def get_key(self):
                return "java"

            def get_version(self):
                return "1.8"

        class MockContainer:
            def __init__(self):
                self.language = MockLanguage()

        class MockFeature:
            def __init__(self):
                self._container = MockContainer()
                self.id = "nameProperty"

            def get_container(self):
                return self._container

        feature = MockFeature()
        mp = MetaPointer.from_feature(feature)

        self.assertEqual("java", mp.language)
        self.assertEqual("1.8", mp.version)
        self.assertEqual("nameProperty", mp.key)  # Falls back to id

    def test_thread_safety(self):
        """Test thread safety of the interning mechanism."""
        results = []
        lv = LanguageVersion("java", "1.8")

        def create_meta_pointer():
            """Create a MetaPointer instance in a thread."""
            mp = MetaPointer(lv, "String")
            results.append(mp)
            time.sleep(0.001)  # Small delay to encourage race conditions

        # Create multiple threads that create the same MetaPointer
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_meta_pointer) for _ in range(20)]
            # Wait for all threads to complete
            for future in futures:
                future.result()

        # All instances should be the same object
        first_instance = results[0]
        for instance in results[1:]:
            self.assertIs(first_instance, instance)

        # Cache should contain only one instance
        self.assertEqual(1, MetaPointer.cache_size())

    def test_multiple_instances_thread_safety(self):
        """Test thread safety with multiple different instances."""
        results = {}

        def create_different_pointers(thread_id):
            """Create different MetaPointer instances in each thread."""
            lv1 = LanguageVersion("java", "1.8")
            lv2 = LanguageVersion("kotlin", "1.9")

            pointers = [
                MetaPointer(lv1, "String"),
                MetaPointer(lv1, "Integer"),
                MetaPointer(lv2, "String"),
                MetaPointer(lv1, "String"),  # Duplicate
            ]
            results[thread_id] = pointers

        # Create multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_different_pointers, i) for i in range(5)]
            # Wait for all threads to complete
            for future in futures:
                future.result()

        # Check that same parameters result in same instances across threads
        java_string_instances = []
        java_integer_instances = []
        kotlin_string_instances = []

        for thread_results in results.values():
            java_string_instances.append(thread_results[0])  # java String
            java_integer_instances.append(thread_results[1])  # java Integer
            kotlin_string_instances.append(thread_results[2])  # kotlin String
            java_string_instances.append(thread_results[3])  # java String duplicate

        # All java String instances should be the same object
        first_java_string = java_string_instances[0]
        for java_string_instance in java_string_instances[1:]:
            self.assertIs(first_java_string, java_string_instance)

        # All java Integer instances should be the same object
        first_java_integer = java_integer_instances[0]
        for java_integer_instance in java_integer_instances[1:]:
            self.assertIs(first_java_integer, java_integer_instance)

        # All kotlin String instances should be the same object
        first_kotlin_string = kotlin_string_instances[0]
        for kotlin_string_instance in kotlin_string_instances[1:]:
            self.assertIs(first_kotlin_string, kotlin_string_instance)

        # Cache should contain exactly 3 instances
        self.assertEqual(3, MetaPointer.cache_size())

    def test_integration_with_language_version_interning(self):
        """Test integration between MetaPointer and LanguageVersion interning."""
        # Create multiple MetaPointers with same language but different keys
        mp1 = MetaPointer(LanguageVersion("java", "1.8"), "String")
        mp2 = MetaPointer(LanguageVersion("java", "1.8"), "Integer")
        mp3 = MetaPointer(LanguageVersion("java", "1.8"), "Boolean")

        # All should share the same LanguageVersion instance
        self.assertIs(mp1.language_version, mp2.language_version)
        self.assertIs(mp2.language_version, mp3.language_version)

        # But MetaPointer instances should be different
        self.assertIsNot(mp1, mp2)
        self.assertIsNot(mp2, mp3)

        # LanguageVersion cache should have 1 entry
        self.assertEqual(1, LanguageVersion.cache_size())
        # MetaPointer cache should have 3 entries
        self.assertEqual(3, MetaPointer.cache_size())

    def test_performance_with_interning(self):
        """Test that interning provides performance benefits."""
        lv = LanguageVersion("java", "1.8")

        # Create many instances with same parameters
        instances = [MetaPointer(lv, "String") for _ in range(1000)]

        # All should be the same object
        first_instance = instances[0]
        for instance in instances[1:]:
            self.assertIs(first_instance, instance)

        # Cache should contain only one MetaPointer instance
        self.assertEqual(1, MetaPointer.cache_size())


if __name__ == "__main__":
    unittest.main()
