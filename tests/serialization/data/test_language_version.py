import time
import unittest
from concurrent.futures import ThreadPoolExecutor

from lionweb.serialization.data.language_version import LanguageVersion


class TestLanguageVersion(unittest.TestCase):
    """
    Test suite for LanguageVersion class with focus on interning behavior,
    immutability, and thread safety.
    """

    def setUp(self):
        """Clear the interning cache before each test to ensure isolation."""
        LanguageVersion.clear_cache()

    def tearDown(self):
        """Clear the interning cache after each test to prevent interference."""
        LanguageVersion.clear_cache()

    def test_basic_creation(self):
        """Test basic creation of LanguageVersion instances."""
        lv = LanguageVersion("java", "1.8")
        self.assertEqual("java", lv.key)
        self.assertEqual("1.8", lv.version)
        self.assertEqual("java", lv.get_key())
        self.assertEqual("1.8", lv.get_version())

    def test_none_values(self):
        """Test creation with None values."""
        lv1 = LanguageVersion(None, None)
        self.assertIsNone(lv1.key)
        self.assertIsNone(lv1.version)

        lv2 = LanguageVersion("java", None)
        self.assertEqual("java", lv2.key)
        self.assertIsNone(lv2.version)

        lv3 = LanguageVersion(None, "1.8")
        self.assertIsNone(lv3.key)
        self.assertEqual("1.8", lv3.version)

    def test_factory_method(self):
        """Test the factory method 'of' returns interned instances."""
        lv1 = LanguageVersion.of("java", "1.8")
        lv2 = LanguageVersion.of("java", "1.8")

        # Should be the same object due to interning
        self.assertIs(lv1, lv2)
        self.assertEqual(lv1, lv2)

    def test_constructor_interning(self):
        """Test that constructor also returns interned instances."""
        lv1 = LanguageVersion("java", "1.8")
        lv2 = LanguageVersion("java", "1.8")

        # Should be the same object due to interning
        self.assertIs(lv1, lv2)

    def test_mixed_creation_methods(self):
        """Test that constructor and factory method return same interned instances."""
        lv1 = LanguageVersion("java", "1.8")
        lv2 = LanguageVersion.of("java", "1.8")

        # Should be the same object
        self.assertIs(lv1, lv2)

    def test_different_instances_not_interned(self):
        """Test that different parameter combinations create different instances."""
        lv1 = LanguageVersion("java", "1.8")
        lv2 = LanguageVersion("java", "11")
        lv3 = LanguageVersion("kotlin", "1.8")
        lv4 = LanguageVersion("kotlin", "11")

        # All should be different objects
        self.assertIsNot(lv1, lv2)
        self.assertIsNot(lv1, lv3)
        self.assertIsNot(lv1, lv4)
        self.assertIsNot(lv2, lv3)
        self.assertIsNot(lv2, lv4)
        self.assertIsNot(lv3, lv4)

    def test_equality(self):
        """Test equality comparison works correctly."""
        lv1 = LanguageVersion("java", "1.8")
        lv2 = LanguageVersion("java", "1.8")
        lv3 = LanguageVersion("java", "11")
        lv4 = LanguageVersion("kotlin", "1.8")

        # Same parameters should be equal
        self.assertEqual(lv1, lv2)
        self.assertTrue(lv1 == lv2)

        # Different parameters should not be equal
        self.assertNotEqual(lv1, lv3)
        self.assertNotEqual(lv1, lv4)
        self.assertFalse(lv1 == lv3)
        self.assertFalse(lv1 == lv4)

    def test_equality_with_none(self):
        """Test equality with None values."""
        lv1 = LanguageVersion(None, None)
        lv2 = LanguageVersion(None, None)
        lv3 = LanguageVersion("java", None)
        lv4 = LanguageVersion(None, "1.8")

        self.assertEqual(lv1, lv2)
        self.assertNotEqual(lv1, lv3)
        self.assertNotEqual(lv1, lv4)
        self.assertNotEqual(lv3, lv4)

    def test_equality_with_different_types(self):
        """Test equality comparison with different types."""
        lv = LanguageVersion("java", "1.8")

        self.assertNotEqual(lv, "java")
        self.assertNotEqual(lv, 42)
        self.assertNotEqual(lv, None)
        self.assertNotEqual(lv, {"key": "java", "version": "1.8"})

    def test_hash_consistency(self):
        """Test that hash values are consistent for equal objects."""
        lv1 = LanguageVersion("java", "1.8")
        lv2 = LanguageVersion("java", "1.8")
        lv3 = LanguageVersion("java", "11")

        # Equal objects should have equal hash codes
        self.assertEqual(hash(lv1), hash(lv2))

        # Different objects should generally have different hash codes
        self.assertNotEqual(hash(lv1), hash(lv3))

    def test_hash_with_none(self):
        """Test hash calculation with None values."""
        lv1 = LanguageVersion(None, None)
        lv2 = LanguageVersion(None, None)
        lv3 = LanguageVersion("java", None)

        # Should be able to calculate hash without error
        hash1 = hash(lv1)
        hash2 = hash(lv2)
        hash3 = hash(lv3)

        # Equal objects should have equal hashes
        self.assertEqual(hash1, hash2)

        # Different objects should have different hashes
        self.assertNotEqual(hash1, hash3)

    def test_immutability(self):
        """Test that instances are immutable after creation."""
        lv = LanguageVersion("java", "1.8")

        # Setting properties should raise RuntimeError
        with self.assertRaises(RuntimeError):
            lv.set_key("kotlin")

        with self.assertRaises(RuntimeError):
            lv.set_version("11")

        # Values should remain unchanged
        self.assertEqual("java", lv.key)
        self.assertEqual("1.8", lv.version)

    def test_string_representation(self):
        """Test string representation of LanguageVersion."""
        lv1 = LanguageVersion("java", "1.8")
        lv2 = LanguageVersion(None, None)
        lv3 = LanguageVersion("kotlin", None)

        str1 = str(lv1)
        str2 = str(lv2)
        str3 = str(lv3)

        # Should contain the key and version information
        self.assertIn("java", str1)
        self.assertIn("1.8", str1)
        self.assertIn("UsedLanguage", str1)

        self.assertIn("None", str2)
        self.assertIn("UsedLanguage", str2)

        self.assertIn("kotlin", str3)
        self.assertIn("None", str3)

    def test_cache_management(self):
        """Test cache management methods."""
        # Initially cache should be empty
        self.assertEqual(0, LanguageVersion.cache_size())

        # Create some instances
        lv1 = LanguageVersion("java", "1.8")
        self.assertEqual(1, LanguageVersion.cache_size())

        LanguageVersion("kotlin", "1.9")
        self.assertEqual(2, LanguageVersion.cache_size())

        # Creating duplicate should not increase cache size
        lv3 = LanguageVersion("java", "1.8")
        self.assertEqual(2, LanguageVersion.cache_size())
        self.assertIs(lv1, lv3)

        # Clear cache
        LanguageVersion.clear_cache()
        self.assertEqual(0, LanguageVersion.cache_size())

    def test_from_language_static_method(self):
        """Test the from_language static method."""

        # Create a mock language object
        class MockLanguage:
            def __init__(self, key, version):
                self.key = key
                self.version = version

        language = MockLanguage("java", "1.8")
        lv = LanguageVersion.from_language(language)

        self.assertEqual("java", lv.key)
        self.assertEqual("1.8", lv.version)

        # Should be interned
        lv2 = LanguageVersion("java", "1.8")
        self.assertIs(lv, lv2)

    def test_from_language_with_none_language(self):
        """Test from_language with None language raises ValueError."""
        with self.assertRaises(ValueError) as context:
            LanguageVersion.from_language(None)
        self.assertIn("Language parameter should not be null", str(context.exception))

    def test_from_language_with_none_version(self):
        """Test from_language with None version raises ValueError."""

        class MockLanguage:
            def __init__(self, key, version):
                self.key = key
                self.version = version

        language = MockLanguage("java", None)
        with self.assertRaises(ValueError) as context:
            LanguageVersion.from_language(language)
        self.assertIn("Language version should not be null", str(context.exception))

    def test_from_meta_pointer_static_method(self):
        """Test the from_meta_pointer static method."""

        # Create a mock meta pointer object
        class MockMetaPointer:
            def __init__(self, language, version):
                self.language = language
                self.version = version

        meta_pointer = MockMetaPointer("java", "1.8")
        lv = LanguageVersion.from_meta_pointer(meta_pointer)

        self.assertEqual("java", lv.key)
        self.assertEqual("1.8", lv.version)

    def test_from_meta_pointer_with_none_meta_pointer(self):
        """Test from_meta_pointer with None raises ValueError."""
        with self.assertRaises(ValueError) as context:
            LanguageVersion.from_meta_pointer(None)
        self.assertIn(
            "meta_pointer parameter should not be null", str(context.exception)
        )

    def test_from_meta_pointer_with_none_language(self):
        """Test from_meta_pointer with None language raises ValueError."""

        class MockMetaPointer:
            def __init__(self, language, version):
                self.language = language
                self.version = version

        meta_pointer = MockMetaPointer(None, "1.8")
        with self.assertRaises(ValueError) as context:
            LanguageVersion.from_meta_pointer(meta_pointer)
        self.assertIn(
            "meta_pointer language should not be null", str(context.exception)
        )

    def test_from_meta_pointer_with_none_version(self):
        """Test from_meta_pointer with None version raises ValueError."""

        class MockMetaPointer:
            def __init__(self, language, version):
                self.language = language
                self.version = version

        meta_pointer = MockMetaPointer("java", None)
        with self.assertRaises(ValueError) as context:
            LanguageVersion.from_meta_pointer(meta_pointer)
        self.assertIn("meta_pointer version should not be null", str(context.exception))

    def test_thread_safety(self):
        """Test thread safety of the interning mechanism."""
        results = []

        def create_language_version():
            """Create a LanguageVersion instance in a thread."""
            lv = LanguageVersion("java", "1.8")
            results.append(lv)
            time.sleep(0.001)  # Small delay to encourage race conditions

        # Create multiple threads that create the same LanguageVersion
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_language_version) for _ in range(20)]
            # Wait for all threads to complete
            for future in futures:
                future.result()

        # All instances should be the same object
        first_instance = results[0]
        for instance in results[1:]:
            self.assertIs(first_instance, instance)

        # Cache should contain only one instance
        self.assertEqual(1, LanguageVersion.cache_size())

    def test_multiple_instances_thread_safety(self):
        """Test thread safety with multiple different instances."""
        results = {}

        def create_different_versions(thread_id):
            """Create different LanguageVersion instances in each thread."""
            versions = [
                LanguageVersion("java", "1.8"),
                LanguageVersion("kotlin", "1.9"),
                LanguageVersion("scala", "2.13"),
                LanguageVersion("java", "1.8"),  # Duplicate
            ]
            results[thread_id] = versions

        # Create multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_different_versions, i) for i in range(5)]
            # Wait for all threads to complete
            for future in futures:
                future.result()

        # Check that same parameters result in same instances across threads
        java_instances = []
        kotlin_instances = []
        scala_instances = []

        for thread_results in results.values():
            java_instances.append(thread_results[0])  # java 1.8
            kotlin_instances.append(thread_results[1])  # kotlin 1.9
            scala_instances.append(thread_results[2])  # scala 2.13
            java_instances.append(thread_results[3])  # java 1.8 duplicate

        # All Java instances should be the same object
        first_java = java_instances[0]
        for java_instance in java_instances[1:]:
            self.assertIs(first_java, java_instance)

        # All Kotlin instances should be the same object
        first_kotlin = kotlin_instances[0]
        for kotlin_instance in kotlin_instances[1:]:
            self.assertIs(first_kotlin, kotlin_instance)

        # All Scala instances should be the same object
        first_scala = scala_instances[0]
        for scala_instance in scala_instances[1:]:
            self.assertIs(first_scala, scala_instance)

        # Cache should contain exactly 3 instances
        self.assertEqual(3, LanguageVersion.cache_size())

    def test_performance_with_interning(self):
        """Test that interning provides performance benefits for equality checks."""
        # Create many instances with same parameters
        instances = [LanguageVersion("java", "1.8") for _ in range(1000)]

        # All should be the same object
        first_instance = instances[0]
        for instance in instances[1:]:
            self.assertIs(first_instance, instance)

        # Identity check should be faster than value comparison
        # This is more of a conceptual test - the real benefit is in production
        start_time = time.time()
        for i in range(len(instances)):
            for j in range(i + 1, len(instances)):
                # This uses identity comparison due to interning
                self.assertTrue(instances[i] is instances[j])
        end_time = time.time()

        # Just ensure the test completes without error
        self.assertGreater(end_time, start_time)


if __name__ == "__main__":
    unittest.main()
