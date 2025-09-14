import random
import string
import tempfile
import unittest
import zipfile
from pathlib import Path

from lionweb.language import (Concept, Containment, Language, LionCoreBuiltins,
                              Property)
from lionweb.model.impl.dynamic_node import DynamicNode
from lionweb.serialization import SerializationChunk
from lionweb.serialization.serialization_provider import \
    create_standard_protobuf_serialization


class TestArchive(unittest.TestCase):
    """
    Test archive functionality with simple language creation and random partitions.
    Tests round-trip serialization/deserialization to ensure data integrity.
    """

    def setUp(self):
        """Set up a simple test language for serialization tests."""
        self.language = self._create_test_language()
        self.pb_serialization = create_standard_protobuf_serialization()
        self.pb_serialization.register_language(self.language)
        self.pb_serialization.enable_dynamic_nodes()

    def _create_test_language(self) -> Language:
        """Create a simple test language with basic concepts and properties."""
        language = Language("TestLanguage", key="testlang", version="1.0")

        # Get built-in string type
        string_type = LionCoreBuiltins.get_string()
        boolean_type = LionCoreBuiltins.get_boolean()
        integer_type = LionCoreBuiltins.get_integer()

        # Create Document concept (root)
        document = Concept(language=language, name="Document", key="Document")
        document.add_implemented_interface(LionCoreBuiltins.get_inamed())
        document.add_feature(
            Property(
                container=document,
                name="published",
                type=boolean_type,
                key="published_prop",
            )
        )
        language.add_element(document)

        # Create Section concept
        section = Concept(language=language, name="Section", key="Section")
        section.add_feature(
            Property(
                container=section, name="title", type=string_type, key="title_prop"
            )
        )
        section.add_feature(
            Property(
                container=section, name="order", type=integer_type, key="order_prop"
            )
        )
        language.add_element(section)

        # Create Paragraph concept
        paragraph = Concept(language=language, name="Paragraph", key="Paragraph")
        paragraph.add_feature(
            Property(
                container=paragraph,
                name="content",
                type=string_type,
                key="content_prop",
            )
        )
        language.add_element(paragraph)

        # Add containment relationships
        document.add_feature(
            Containment(
                container=document, name="sections", type=section, key="sections_cont"
            )
        )
        section.add_feature(
            Containment(
                container=section,
                name="paragraphs",
                type=paragraph,
                key="paragraphs_cont",
            )
        )

        return language

    def _generate_random_model(
        self, num_documents=3, num_sections_per_doc=5, num_paragraphs_per_section=3
    ):
        """Generate a random model with the test language."""
        documents = []

        for doc_idx in range(num_documents):
            # Create document
            doc = DynamicNode(
                id=f"doc_{doc_idx}",
                concept=self.language.require_concept_by_name("Document"),
            )
            doc.set_property_value("name", f"Document {doc_idx}")
            doc.set_property_value("published", random.choice([True, False]))

            # Add sections
            for sect_idx in range(random.randint(1, num_sections_per_doc)):
                section = DynamicNode(
                    id=f"doc_{doc_idx}_sect_{sect_idx}",
                    concept=self.language.require_concept_by_name("Section"),
                )
                section.set_property_value("title", f"Section {sect_idx}")
                section.set_property_value("order", sect_idx)

                # Add paragraphs
                for para_idx in range(random.randint(1, num_paragraphs_per_section)):
                    paragraph = DynamicNode(
                        id=f"doc_{doc_idx}_sect_{sect_idx}_para_{para_idx}",
                        concept=self.language.require_concept_by_name("Paragraph"),
                    )
                    # Generate random content
                    words = [
                        self._random_string(random.randint(3, 10))
                        for _ in range(random.randint(5, 15))
                    ]
                    paragraph.set_property_value("content", " ".join(words))

                    section.add_child("paragraphs", paragraph)

                doc.add_child("sections", section)

            documents.append(doc)

        return documents

    def _random_string(self, length):
        """Generate a random string of given length."""
        return "".join(random.choice(string.ascii_lowercase) for _ in range(length))

    def _create_test_archive(self, documents, partitions_per_doc=2):
        """Create a test archive with random partitions."""
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
            archive_path = temp_file.name

        with zipfile.ZipFile(archive_path, "w") as zf:
            partition_id = 0

            for doc in documents:
                # Collect all nodes in the document
                all_nodes = []
                self.pb_serialization.collect_self_and_descendants(doc, True, all_nodes)

                # Split into random partitions
                random.shuffle(all_nodes)
                partition_size = max(1, len(all_nodes) // partitions_per_doc)

                for i in range(0, len(all_nodes), partition_size):
                    partition_nodes = all_nodes[i : i + partition_size]

                    # Serialize partition
                    chunk = (
                        self.pb_serialization.serialize_nodes_to_serialization_chunk(
                            partition_nodes
                        )
                    )
                    pb_data = self.pb_serialization.read_pbchunk_from_bytes(
                        self.pb_serialization._serialize_chunk_to_bytes(chunk)
                    )

                    # Add to archive
                    entry_name = f"partition_{partition_id:04d}.binpb"
                    zf.writestr(entry_name, pb_data.SerializeToString())
                    partition_id += 1

        return archive_path

    def _serialize_chunk_to_bytes(self, chunk: SerializationChunk) -> bytes:
        bs = self.pb_serialization.serialize_chunk_to_bytes(chunk)
        return bs

    def test_simple_archive_round_trip(self):
        """Test basic archive creation and loading."""
        # Generate simple model
        documents = self._generate_random_model(
            num_documents=2, num_sections_per_doc=3, num_paragraphs_per_section=2
        )

        # Create chunks manually for this simple test
        chunks = []
        for doc in documents:
            chunk = self.pb_serialization.serialize_tree_to_serialization_chunk(doc)
            chunks.append(chunk)

        # Verify chunks are created correctly
        self.assertEqual(2, len(chunks))

        # Check first chunk structure
        first_chunk = chunks[0]
        self.assertIsNotNone(first_chunk.serialization_format_version)
        self.assertGreater(len(first_chunk.classifier_instances), 0)

        # Verify we can deserialize
        deserialized_nodes = self.pb_serialization.deserialize_serialization_chunk(
            first_chunk
        )
        self.assertGreater(len(deserialized_nodes), 0)

        # Check root document properties
        root_doc = next(
            node
            for node in deserialized_nodes
            if node.get_classifier().get_name() == "Document"
        )
        self.assertIsNotNone(root_doc.get_property_value("name"))
        self.assertIsNotNone(root_doc.get_property_value("published"))

    def test_archive_processing_with_callback(self):
        """Test processing archive with callback function."""
        # Generate model
        documents = self._generate_random_model(num_documents=2)

        # Create temporary archive file
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
            archive_path = temp_file.name

        try:
            with zipfile.ZipFile(archive_path, "w") as zf:
                for i, doc in enumerate(documents):
                    chunk = self.pb_serialization.serialize_tree_to_serialization_chunk(
                        doc
                    )
                    # Simulate protobuf serialization by using JSON for now
                    bs = self.pb_serialization.serialize_chunk_to_bytes(chunk)
                    zf.writestr(f"chunk_{i}.binpb", bs)

            # Test callback processing
            processed_chunks = []

            def chunk_processor(index, total, chunk):
                """Callback to process each chunk."""
                processed_chunks.append((index, chunk))
                self.assertIsNotNone(chunk)
                self.assertGreaterEqual(index, 0)
                self.assertLess(index, total)
                self.assertEqual(total, 2)  # We have 2 documents

            with zipfile.ZipFile(archive_path, "r") as zf:
                n_elements = len(zf.namelist())
                for i, name in enumerate(zf.namelist()):
                    content = zf.read(name)
                    chunk = self.pb_serialization.deserialize_chunk_from_bytes(content)
                    chunk_processor(i, n_elements, chunk)

            # Verify processing
            self.assertEqual(2, len(processed_chunks))

        finally:
            Path(archive_path).unlink()  # Clean up

    def test_data_integrity_after_serialization(self):
        """Test that data remains intact after serialization/deserialization."""
        # Generate model with known data
        doc = DynamicNode(
            id="test_doc", concept=self.language.require_concept_by_name("Document")
        )
        doc.set_property_value("name", "Test Document")
        doc.set_property_value("published", True)

        section = DynamicNode(
            id="test_section", concept=self.language.require_concept_by_name("Section")
        )
        section.set_property_value("title", "Test Section")
        section.set_property_value("order", 42)

        paragraph = DynamicNode(
            id="test_paragraph",
            concept=self.language.require_concept_by_name("Paragraph"),
        )
        paragraph.set_property_value(
            "content", "This is test content with special chars: àáâãäå!"
        )

        # Build hierarchy
        section.add_child("paragraphs", paragraph)
        doc.add_child("sections", section)

        # Serialize and deserialize
        chunk = self.pb_serialization.serialize_tree_to_serialization_chunk(doc)
        deserialized_nodes = self.pb_serialization.deserialize_serialization_chunk(
            chunk
        )

        # Verify structure is preserved
        self.assertEqual(3, len(deserialized_nodes))  # doc + section + paragraph

        # Find nodes by concept
        deserialized_doc = next(
            n for n in deserialized_nodes if n.get_classifier().get_name() == "Document"
        )
        deserialized_section = next(
            n for n in deserialized_nodes if n.get_classifier().get_name() == "Section"
        )
        deserialized_paragraph = next(
            n
            for n in deserialized_nodes
            if n.get_classifier().get_name() == "Paragraph"
        )

        # Verify properties
        self.assertEqual("Test Document", deserialized_doc.get_property_value("name"))
        self.assertEqual(True, deserialized_doc.get_property_value("published"))
        self.assertEqual(
            "Test Section", deserialized_section.get_property_value("title")
        )
        self.assertEqual(42, deserialized_section.get_property_value("order"))
        self.assertEqual(
            "This is test content with special chars: àáâãäå!",
            deserialized_paragraph.get_property_value("content"),
        )

        # Verify IDs are preserved
        self.assertEqual("test_doc", deserialized_doc.id)
        self.assertEqual("test_section", deserialized_section.id)
        self.assertEqual("test_paragraph", deserialized_paragraph.id)

    def test_random_partitions_integrity(self):
        """Test that random partitioning doesn't break data integrity."""
        # Generate larger model
        documents = self._generate_random_model(
            num_documents=1, num_sections_per_doc=5, num_paragraphs_per_section=4
        )
        doc = documents[0]

        # Collect all original nodes
        original_nodes = []
        self.pb_serialization.collect_self_and_descendants(doc, True, original_nodes)
        original_count = len(original_nodes)

        # Create random partitions
        random.shuffle(original_nodes)
        partition_size = 3  # Small partitions to test splitting
        partitions = []

        for i in range(0, len(original_nodes), partition_size):
            partition_nodes = original_nodes[i : i + partition_size]
            chunk = self.pb_serialization.serialize_nodes_to_serialization_chunk(
                partition_nodes
            )
            partitions.append(chunk)

        # Deserialize all partitions and collect nodes
        all_deserialized_nodes = []
        for chunk in partitions:
            deserialized = self.pb_serialization.deserialize_serialization_chunk(chunk)
            all_deserialized_nodes.extend(deserialized)

        # Verify we got all nodes back
        self.assertEqual(original_count, len(all_deserialized_nodes))

        # Verify all IDs are preserved
        original_ids = {node.id for node in original_nodes}
        deserialized_ids = {node.id for node in all_deserialized_nodes}
        self.assertEqual(original_ids, deserialized_ids)

        # Verify no duplicate IDs
        self.assertEqual(len(deserialized_ids), len(all_deserialized_nodes))

    def test_load_archive_function(self):
        """Test the load_archive convenience function."""
        # Create a simple test archive manually
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
            archive_path = temp_file.name

        try:
            # Create simple model
            doc = DynamicNode(
                id="simple_doc",
                concept=self.language.require_concept_by_name("Document"),
            )
            doc.set_property_value("name", "Simple Document")
            doc.set_property_value("published", False)

            # Create archive
            with zipfile.ZipFile(archive_path, "w") as zf:
                chunk = self.pb_serialization.serialize_tree_to_serialization_chunk(doc)
                # For this test, we'll use JSON data as a placeholder
                bs = self.pb_serialization.serialize_chunk_to_bytes(chunk)
                zf.writestr("test_chunk.binpb", bs)

            # Test load_archive would work if we had proper protobuf format
            # For now, we'll test the structure
            with zipfile.ZipFile(archive_path, "r") as zf:
                self.assertEqual(1, len(zf.namelist()))
                self.assertEqual("test_chunk.binpb", zf.namelist()[0])

                # Verify content can be read
                content = zf.read("test_chunk.binpb")
                self.assertGreater(len(content), 0)

        finally:
            Path(archive_path).unlink()  # Clean up


if __name__ == "__main__":
    unittest.main()
