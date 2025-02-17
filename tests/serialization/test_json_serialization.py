import json
import unittest
from enum import Enum
from pathlib import Path

from serialization.library.book import Book
from serialization.library.guide_book_writer import GuideBookWriter
from serialization.library.library import Library
from serialization.library.library_language import LibraryLanguage
from serialization.refsmm.container_node import ContainerNode
from serialization.refsmm.ref_node import RefNode
from serialization.refsmm.refs_language import RefsLanguage
from serialization.serialization_test import SerializationTest
from serialization.simplemath.int_literal import IntLiteral
from serialization.simplemath.simple_math_language import SimpleMathLanguage
from serialization.simplemath.sum import Sum

from lionwebpython.api.unresolved_classifier_instance_exception import \
    UnresolvedClassifierInstanceException
from lionwebpython.language import Annotation, Concept, Language, Property
from lionwebpython.language.enumeration import Enumeration
from lionwebpython.language.enumeration_literal import EnumerationLiteral
from lionwebpython.language.lioncore_builtins import LionCoreBuiltins
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.classifier_instance_utils import \
    ClassifierInstanceUtils
from lionwebpython.model.impl.dynamic_annotation_instance import \
    DynamicAnnotationInstance
from lionwebpython.model.impl.dynamic_node import DynamicNode
from lionwebpython.model.impl.enumeration_value_impl import \
    EnumerationValueImpl
from lionwebpython.model.impl.proxy_node import ProxyNode
from lionwebpython.model.reference_value import ReferenceValue
from lionwebpython.serialization.data.metapointer import MetaPointer
from lionwebpython.serialization.deserialization_exception import \
    DeserializationException
from lionwebpython.serialization.json_serialization import JsonSerialization
from lionwebpython.serialization.serialization_provider import \
    SerializationProvider
from lionwebpython.serialization.serialized_json_comparison_utils import \
    SerializedJsonComparisonUtils
from lionwebpython.serialization.unavailable_node_policy import \
    UnavailableNodePolicy
from lionwebpython.utils.language_validator import LanguageValidator


class MyEnum(Enum):
    el1 = "el1"
    el2 = "el2"


class JsonSerializationTest(SerializationTest):

    def test_serialize_reference_without_resolve_info(self):
        book = DynamicNode("foo123", LibraryLanguage.BOOK)
        writer = DynamicNode("-Arthur-Foozillus-id-", LibraryLanguage.WRITER)
        book.add_reference_value(
            LibraryLanguage.BOOK.get_reference_by_name("author"),
            ReferenceValue(referred=writer, resolve_info=None),
        )

        json_serialization = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        json_serialization.keep_null_properties = True
        json_serialization.primitive_values_serialization.register_serializer(
            "string_id", str
        )
        json_serialization.primitive_values_serialization.register_serializer(
            "int_id", str
        )

        serialized = json_serialization.serialize_nodes_to_json_element([book])
        with open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "foo-library.json",
            "r",
        ) as f:
            expected = json.load(f)

        SerializedJsonComparisonUtils.assert_equivalent_lionweb_json(
            expected, serialized
        )

    def test_serialize_multiple_subtrees(self):
        bobs_library = Library("bl", "Bob's Library")
        jack_london = GuideBookWriter("jl", "Jack London")
        jack_london.set_countries("Alaska")
        explorer_book = Book("eb", "Explorer Book", jack_london)
        bobs_library.add_book(explorer_book)

        json_serialization = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        json_serialization.keep_null_properties = True
        json_serialization.primitive_values_serialization.register_serializer(
            "string_id", str
        )
        json_serialization.primitive_values_serialization.register_serializer(
            "int_id", str
        )

        serialized = json_serialization.serialize_trees_to_json_element(
            [bobs_library, jack_london]
        )
        with open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "bobslibrary.json",
            "r",
        ) as f:
            expected = json.load(f)

        SerializedJsonComparisonUtils.assert_equivalent_lionweb_json(
            expected, serialized
        )

    def test_serialize_multiple_subtrees_skip_duplicate_nodes(self):
        bobs_library = Library("bl", "Bob's Library")
        jack_london = GuideBookWriter("jl", "Jack London")
        jack_london.set_countries("Alaska")
        explorer_book = Book("eb", "Explorer Book", jack_london)
        bobs_library.add_book(explorer_book)

        # The library MM is not using standard primitive types but its own, so we need to specify how to serialize
        json_serialization = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        json_serialization.keep_null_properties = True
        json_serialization.primitive_values_serialization.register_serializer(
            "INhBvWyXvxwNsePuX0rdNGB_J9hi85cTb1Q0APXCyJ0", lambda value: value
        )
        json_serialization.primitive_values_serialization.register_serializer(
            "gVp8_QSmXE2k4pd-sQZgjYMoW95SLLaVIH4yMYqqbt4", lambda value: str(value)
        )

        json_serialized = json_serialization.serialize_nodes_to_json_element(
            [bobs_library, jack_london, explorer_book]
        )

        with open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "bobslibrary.json",
            "r",
        ) as file:
            json_read = json.load(file)

        SerializedJsonComparisonUtils.assert_equivalent_lionweb_json(
            json_read, json_serialized
        )

    def test_deserialize_language_with_enumerations(self):
        with open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "TestLang-language.json",
            "r",
        ) as f:
            json_element = json.load(f)

        json_serialization = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        deserialized_nodes = json_serialization.deserialize_json_to_nodes(json_element)

        test_enum = next(
            n
            for n in deserialized_nodes
            if n.get_id()
            == "MDhjYWFkNzUtODI0Ni00NDI3LWJiNGQtODQ0NGI2YzVjNzI5LzI1ODUzNzgxNjU5NzMyMDQ1ODI"
        )
        self.assertEqual(test_enum.get_name(), "TestEnumeration1")

    def test_deserialize_language_with_dependencies(self):
        json_serialization = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        with open(
            Path(__file__).parent.parent
            / "resources"
            / "properties-example"
            / "starlasu.lmm.json",
            "r",
        ) as file:
            starlasu_nodes = json_serialization.deserialize_json_to_nodes(
                json.load(file)
            )
            starlasu = next(
                node for node in starlasu_nodes if isinstance(node, Language)
            )
            json_serialization.instance_resolver.add_tree(starlasu)

        with open(
            Path(__file__).parent.parent
            / "resources"
            / "properties-example"
            / "properties.lmm.json",
            "r",
        ) as file:
            properties_nodes = json_serialization.deserialize_json_to_nodes(
                json.load(file)
            )
            properties = next(
                node for node in properties_nodes if isinstance(node, Language)
            )

        LanguageValidator.ensure_is_valid(starlasu)
        LanguageValidator.ensure_is_valid(properties)

    def _prepare_deserialization_of_simple_math(
        self, json_serialization: JsonSerialization
    ):
        json_serialization.classifier_resolver.register_language(
            SimpleMathLanguage.INSTANCE
        )

        # Register custom deserializer for IntLiteral
        def deserialize_int_literal(
            concept, serialized_node, deserialized_nodes_by_id, properties_values
        ):
            value = properties_values.get(concept.get_property_by_name("value"))
            return IntLiteral(value, serialized_node.id)

        json_serialization.instantiator.register_custom_deserializer(
            SimpleMathLanguage.INT_LITERAL.id, deserialize_int_literal
        )

        # Register custom deserializer for Sum
        def deserialize_sum(
            concept, serialized_node, deserialized_nodes_by_id, properties_values
        ):
            left_scv = next(
                c
                for c in serialized_node.containments
                if c.meta_pointer.key == "SimpleMath_Sum_left"
            )
            left = deserialized_nodes_by_id.get(left_scv.value[0])

            right_scv = next(
                c
                for c in serialized_node.containments
                if c.meta_pointer.key == "SimpleMath_Sum_right"
            )
            right = deserialized_nodes_by_id.get(right_scv.value[0])

            return Sum(left, right, serialized_node.id)

        json_serialization.instantiator.register_custom_deserializer(
            SimpleMathLanguage.SUM.id, deserialize_sum
        )

    def test_deserialize_multiple_roots(self):
        sum1 = Sum(IntLiteral(1), IntLiteral(2))
        sum2 = Sum(IntLiteral(3), IntLiteral(4))
        js = SerializationProvider.get_standard_json_serialization()
        serialized = js.serialize_trees_to_json_element([sum1, sum2])

        # Check languages and nodes count
        self.assertEqual(len(serialized["languages"]), 2)
        self.assertEqual(len(serialized["nodes"]), 6)

        self._prepare_deserialization_of_simple_math(js)
        deserialized = [
            n for n in js.deserialize_json_to_nodes(serialized) if isinstance(n, Sum)
        ]
        self.assertEqual(deserialized, [sum1, sum2])

    def test_deserialize_nodes_without_ids_in_the_right_order(self):
        il1 = IntLiteral(1, None)
        il2 = IntLiteral(2, None)
        il3 = IntLiteral(3, None)
        il4 = IntLiteral(4, None)
        js = SerializationProvider.get_standard_json_serialization()
        serialized = js.serialize_trees_to_json_element([il1, il2, il3, il4])

        self._prepare_deserialization_of_simple_math(js)
        deserialized = [node for node in js.deserialize_json_to_nodes(serialized)]
        self.assertEqual(deserialized, [il1, il2, il3, il4])

    def test_deserialize_trees_without_ids_in_the_right_order(self):
        il1 = IntLiteral(1, "int_1")
        il2 = IntLiteral(2, "int_2")
        sum1 = Sum(il1, il2, None)
        il3 = IntLiteral(3, "int_3")
        il4 = IntLiteral(4, "int_4")
        sum2 = Sum(il3, il4, None)
        js = SerializationProvider.get_standard_json_serialization()

        serialized = js.serialize_trees_to_json_element([sum1, sum2])
        self._prepare_deserialization_of_simple_math(js)
        deserialized = js.deserialize_json_to_nodes(serialized)

        self.assertEqual(deserialized, [sum1, il1, il2, sum2, il3, il4])

    def test_deserialize_trees_with_arbitrary_order_and_null_ids_in_the_right_order(
        self,
    ):
        # Handling multiple parents with null IDs requires special care as they are ambiguous
        il1 = IntLiteral(1, "int_1")
        il2 = IntLiteral(2, "int_2")
        sum1 = Sum(il1, il2, None)
        il3 = IntLiteral(3, "int_3")
        il4 = IntLiteral(4, "int_4")
        sum2 = Sum(il3, il4, None)

        js = SerializationProvider.get_standard_json_serialization()
        serialized = js.serialize_nodes_to_json_element(
            [il4, il1, sum1, il2, sum2, il3]
        )
        self._prepare_deserialization_of_simple_math(js)
        deserialized = js.deserialize_json_to_nodes(serialized)

        self.assertEqual(deserialized, [il4, il1, sum1, il2, sum2, il3])

    def test_deserialize_children_with_null_id(self):
        # Expecting DeserializationException
        il1 = IntLiteral(1, "int_1")
        il2 = IntLiteral(2, None)
        # Let's override it, as it gets a random id
        il2.id = None
        sum1 = Sum(il1, il2, None)

        js = SerializationProvider.get_standard_json_serialization()
        serialized = js.serialize_nodes_to_json_element([sum1, il1, il2])
        self._prepare_deserialization_of_simple_math(js)

        with self.assertRaises(DeserializationException):
            js.deserialize_json_to_nodes(serialized)

    def prepare_deserialization_of_refmm(self, js):
        js.classifier_resolver.register_language(RefsLanguage.INSTANCE)
        js.instantiator.register_custom_deserializer(
            RefsLanguage.CONTAINER_NODE.get_id(),
            lambda concept, serialized_node, deserialized_nodes_by_id, properties_values: ContainerNode(
                properties_values.get(concept.get_containment_by_name("contained")),
                serialized_node.get_id(),
            ),
        )
        js.instantiator.register_custom_deserializer(
            RefsLanguage.REF_NODE.get_id(),
            lambda concept, serialized_node, deserialized_nodes_by_id, properties_values: RefNode(
                serialized_node.get_id()
            ),
        )

    def test_dead_references(self):
        r1 = RefNode()
        r2 = RefNode()
        r1.set_referred(r2)

        js = SerializationProvider.get_standard_json_serialization()
        serialized = js.serialize_nodes_to_json_element([r1])
        self.prepare_deserialization_of_refmm(js)

        with self.assertRaises(DeserializationException):
            js.deserialize_json_to_nodes(serialized)

    def test_references_loop(self):
        r1 = RefNode()
        r2 = RefNode()
        r3 = RefNode()
        r1.set_referred(r2)
        r2.set_referred(r3)
        r3.set_referred(r1)

        js = SerializationProvider.get_standard_json_serialization()
        serialized = js.serialize_nodes_to_json_element([r1, r2, r3])
        self.prepare_deserialization_of_refmm(js)
        deserialized = js.deserialize_json_to_nodes(serialized)

        self.assertEqual(deserialized, [r1, r2, r3])

    def test_containments_loop(self):
        c1 = ContainerNode()
        c2 = ContainerNode()
        c1.set_contained(c2)
        c2.set_contained(c1)
        c2.set_parent(c1)
        c1.set_parent(c2)

        self.assertEqual(c2, c1.get_parent())
        self.assertEqual(c1, c2.get_parent())
        self.assertEqual(ClassifierInstanceUtils.get_children(c1), [c2])
        self.assertEqual(ClassifierInstanceUtils.get_children(c2), [c1])

        js = SerializationProvider.get_standard_json_serialization()
        serialized = js.serialize_nodes_to_json_element([c1, c2])
        self.prepare_deserialization_of_refmm(js)

        with self.assertRaises(DeserializationException):
            js.deserialize_json_to_nodes(serialized)

    def test_deserialize_tree_without_root(self):
        js = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        with self.assertRaises(DeserializationException):
            js.deserialize_json_to_nodes(
                json.load(
                    open(
                        Path(__file__).parent.parent
                        / "resources"
                        / "mpsMeetup-issue10"
                        / "example1.json"
                    )
                )
            )

    def test_serialization_of_enum_literal_using_enumeration_value_instances(self):
        mm = Language("my.language")
        mm.set_id("mm_id")
        mm.set_key("mm_key")
        mm.set_version("1")

        e = Enumeration(language=mm, name="my.enumeration")
        e.set_id("enumeration_id")
        e.set_key("enumeration_key")

        el1 = EnumerationLiteral(enumeration=e, name="el1")
        el1.set_id("el1_id")
        el1.set_key("el1_key")

        el2 = EnumerationLiteral(enumeration=e, name="el2")
        el2.set_id("el2_id")
        el2.set_key("el2_key")

        c = Concept(language=mm, name="my.concept")
        c.set_id("concept_id")
        c.set_key("concept_key")

        p = Property.create_required(name="my.property", type=e)
        p.set_id("property_id")
        p.set_key("property_key")
        c.add_feature(p)

        n1 = DynamicNode("node1", c)
        n1.set_property_value(property=p, value=EnumerationValueImpl(el1))

        n2 = DynamicNode("node2", c)
        n2.set_property_value(property=p, value=EnumerationValueImpl(el2))

        js = SerializationProvider.get_standard_json_serialization()
        js.register_language(mm)

        je = js.serialize_nodes_to_json_element([n1, n2])
        expected_json = json.loads(
            """
            {
                "serializationFormatVersion": "2024.1",
                "languages": [{"version": "1", "key": "mm_key"}],
                "nodes": [
                    {
                        "id": "node1",
                        "classifier": {"language": "mm_key", "version": "1", "key": "concept_key"},
                        "properties": [{"property": {"language": "mm_key", "version": "1", "key": "property_key"}, "value": "el1_key"}],
                        "containments": [],
                        "references": [],
                        "annotations": [],
                        "parent": null
                    },
                    {
                        "id": "node2",
                        "classifier": {"language": "mm_key", "version": "1", "key": "concept_key"},
                        "properties": [{"property": {"language": "mm_key", "version": "1", "key": "property_key"}, "value": "el2_key"}],
                        "containments": [],
                        "references": [],
                        "annotations": [],
                        "parent": null
                    }
                ]
            }
        """
        )

        self.assertEqual(je, expected_json)

    def test_serialization_of_enum_literal_using_enum_instances(self):
        mm = Language("my.language")
        mm.set_id("mm_id")
        mm.set_key("mm_key")
        mm.set_version("1")

        e = Enumeration(language=mm, name="my.enumeration")
        e.set_id("enumeration_id")
        e.set_key("enumeration_key")

        el1 = EnumerationLiteral(enumeration=e, name="el1")
        el1.set_id("el1_id")
        el1.set_key("el1_key")

        el2 = EnumerationLiteral(enumeration=e, name="el2")
        el2.set_id("el2_id")
        el2.set_key("el2_key")

        c = Concept(language=mm, name="my.concept")
        c.set_id("concept_id")
        c.set_key("concept_key")

        p = Property.create_required(name="my.property", type=e)
        p.set_id("property_id")
        p.set_key("property_key")
        c.add_feature(p)

        n1 = DynamicNode("node1", c)
        n1.set_property_value(property=p, value=MyEnum.el1)

        n2 = DynamicNode("node2", c)
        n2.set_property_value(property=p, value=MyEnum.el2)

        js = SerializationProvider.get_standard_json_serialization()
        js.register_language(mm)

        je = js.serialize_nodes_to_json_element([n1, n2])
        expected_json = json.loads(
            """
            {
                "serializationFormatVersion": "2024.1",
                "languages": [{"version": "1", "key": "mm_key"}],
                "nodes": [
                    {
                        "id": "node1",
                        "classifier": {"language": "mm_key", "version": "1", "key": "concept_key"},
                        "properties": [{"property": {"language": "mm_key", "version": "1", "key": "property_key"}, "value": "el1_key"}],
                        "containments": [],
                        "references": [],
                        "annotations": [],
                        "parent": null
                    },
                    {
                        "id": "node2",
                        "classifier": {"language": "mm_key", "version": "1", "key": "concept_key"},
                        "properties": [{"property": {"language": "mm_key", "version": "1", "key": "property_key"}, "value": "el2_key"}],
                        "containments": [],
                        "references": [],
                        "annotations": [],
                        "parent": null
                    }
                ]
            }
        """
        )

        self.assertEqual(je, expected_json)

    def test_deserialize_enumeration_literals_using_enumeration_value_instances(self):
        je = json.loads(
            """
            {
                "serializationFormatVersion": "2024.1",
                "languages": [{"version": "1", "key": "mm_key"}],
                "nodes": [
                    {
                        "id": "node1",
                        "classifier": {"language": "mm_key", "version": "1", "key": "concept_key"},
                        "properties": [{"property": {"language": "mm_key", "version": "1", "key": "property_key"}, "value": "el1_key"}],
                        "containments": [],
                        "references": [],
                        "parent": null
                    },
                    {
                        "id": "node2",
                        "classifier": {"language": "mm_key", "version": "1", "key": "concept_key"},
                        "properties": [{"property": {"language": "mm_key", "version": "1", "key": "property_key"}, "value": "el2_key"}],
                        "containments": [],
                        "references": [],
                        "parent": null
                    }
                ]
            }
        """
        )

        mm = Language("my.language")
        mm.set_id("mm_id")
        mm.set_key("mm_key")
        mm.set_version("1")

        e = Enumeration(language=mm, name="my.enumeration")
        e.set_id("enumeration_id")
        e.set_key("enumeration_key")

        el1 = EnumerationLiteral(enumeration=e, name="el1")
        el1.set_id("el1_id")
        el1.set_key("el1_key")

        el2 = EnumerationLiteral(enumeration=e, name="el2")
        el2.set_id("el2_id")
        el2.set_key("el2_key")

        c = Concept(language=mm, name="my.concept")
        c.set_id("concept_id")
        c.set_key("concept_key")

        p = Property.create_required(name="my.property", type=e)
        p.set_id("property_id")
        p.set_key("property_key")
        c.add_feature(p)

        n1 = DynamicNode("node1", c)
        n1.set_property_value(property=p, value=EnumerationValueImpl(el1))

        n2 = DynamicNode("node2", c)
        n2.set_property_value(property=p, value=EnumerationValueImpl(el2))

        js = SerializationProvider.get_standard_json_serialization()
        js.register_language(mm)
        js.instantiator.enable_dynamic_nodes()
        js.primitive_values_serialization.enable_dynamic_nodes()

        deserialized_nodes = js.deserialize_json_to_nodes(je)
        self.assertEqual([n1, n2], deserialized_nodes)
        self.assertEqual(
            EnumerationValueImpl(el1),
            deserialized_nodes[0].get_property_value(property=p),
        )
        self.assertEqual(
            EnumerationValueImpl(el2),
            deserialized_nodes[1].get_property_value(property=p),
        )

    def test_deserialize_enumeration_literals_using_enum_instances(self):
        je = json.loads(
            """
            {
                "serializationFormatVersion": "2024.1",
                "languages": [{"version": "1", "key": "mm_key"}],
                "nodes": [
                    {
                        "id": "node1",
                        "classifier": {"language": "mm_key", "version": "1", "key": "concept_key"},
                        "properties": [{"property": {"language": "mm_key", "version": "1", "key": "property_key"}, "value": "el1_key"}],
                        "containments": [],
                        "references": [],
                        "parent": null
                    },
                    {
                        "id": "node2",
                        "classifier": {"language": "mm_key", "version": "1", "key": "concept_key"},
                        "properties": [{"property": {"language": "mm_key", "version": "1", "key": "property_key"}, "value": "el2_key"}],
                        "containments": [],
                        "references": [],
                        "parent": null
                    }
                ]
            }
        """
        )

        mm = Language("my.language")
        mm.set_id("mm_id")
        mm.set_key("mm_key")
        mm.set_version("1")

        e = Enumeration(language=mm, name="my.enumeration")
        e.set_id("enumeration_id")
        e.set_key("enumeration_key")

        el1 = EnumerationLiteral(enumeration=e, name="el1")
        el1.set_id("el1_id")
        el1.set_key("el1_key")

        el2 = EnumerationLiteral(enumeration=e, name="el2")
        el2.set_id("el2_id")
        el2.set_key("el2_key")

        c = Concept(language=mm, name="my.concept")
        c.set_id("concept_id")
        c.set_key("concept_key")

        p = Property.create_required(name="my.property", type=e)
        p.set_id("property_id")
        p.set_key("property_key")
        c.add_feature(p)

        n1 = DynamicNode("node1", c)
        n1.set_property_value(property=p, value=MyEnum.el1)

        n2 = DynamicNode("node2", c)
        n2.set_property_value(property=p, value=MyEnum.el2)

        js = SerializationProvider.get_standard_json_serialization()
        js.primitive_values_serialization.register_enum_class(MyEnum, e)
        js.register_language(mm)
        js.instantiator.enable_dynamic_nodes()

        deserialized_nodes = js.deserialize_json_to_nodes(je)
        self.assertEqual([n1, n2], deserialized_nodes)
        self.assertEqual(
            MyEnum.el1, deserialized_nodes[0].get_property_value(property=p)
        )
        self.assertEqual(
            MyEnum.el2, deserialized_nodes[1].get_property_value(property=p)
        )

    def test_serialization_of_language_versions_with_imports(self):
        my_language = Language()
        my_language.set_key("myLanguage-key")
        my_language.set_version("3")

        my_concept = Concept()
        my_concept.add_implemented_interface(LionCoreBuiltins.get_inamed())
        my_language.add_element(my_concept)

        my_instance = DynamicNode("instance-a", my_concept)
        json_ser = SerializationProvider.get_standard_json_serialization()
        json_ser.keep_null_properties = True
        serialized_chunk = json_ser.serialize_nodes_to_serialization_block(
            [my_instance]
        )

        self.assertEqual(1, len(serialized_chunk.get_classifier_instances()))
        serialized_classifier_instance = serialized_chunk.get_classifier_instances()[0]
        self.assertEqual("instance-a", serialized_classifier_instance.get_id())
        self.assertEqual(1, len(serialized_classifier_instance.get_properties()))
        serialized_name = serialized_classifier_instance.get_properties()[0]
        expected_pointer = MetaPointer(
            "LionCore-builtins", "2024.1", "LionCore-builtins-INamed-name"
        )
        self.assertEqual(expected_pointer, serialized_name.get_meta_pointer())

    def test_serialize_annotations(self):
        lang = Language("l", "l", "l", "1")
        a1 = Annotation(language=lang, name="a1", id="a1", key="a1")
        a2 = Annotation(language=lang, name="a2", id="a2", key="a2")
        c = Concept(language=lang, name="c", id="c", key="c")

        n1 = DynamicNode("n1", c)
        DynamicAnnotationInstance(id="a1_1", annotation=a1, annotated=n1)
        DynamicAnnotationInstance(id="a1_2", annotation=a1, annotated=n1)
        DynamicAnnotationInstance(id="a2_3", annotation=a2, annotated=n1)

        hjs = SerializationProvider.get_standard_json_serialization()
        hjs.enable_dynamic_nodes()
        serialized_chunk = hjs.serialize_nodes_to_serialization_block([n1])

        self.assertEqual(4, len(serialized_chunk.get_classifier_instances()))
        serialized_n1 = serialized_chunk.get_classifier_instances()[0]
        self.assertEqual("n1", serialized_n1.get_id())
        self.assertIsNone(serialized_n1.get_parent_node_id())
        self.assertEqual(["a1_1", "a1_2", "a2_3"], serialized_n1.get_annotations())

        deserialized = hjs.deserialize_serialization_block(serialized_chunk)
        self.assertEqual(4, len(deserialized))
        self.assertEqual(n1, deserialized[0])

    def test_serialize_language(self):
        meta_lang = Language("metaLang", "metaLang", "metaLang", "1")
        meta_ann = Annotation(
            language=meta_lang, name="metaAnn", id="metaAnn", key="metaAnn"
        )

        lang = Language("l", "l", "l", "1")
        Annotation(language=lang, name="a1", key="a1", id="a1")
        Annotation(language=lang, name="a2", key="a2", id="a2")
        c = Concept(language=lang, name="c", key="c", id="c")
        ann = DynamicAnnotationInstance("metaAnn_1", meta_ann, c)
        c.add_annotation(ann)

        hjs = SerializationProvider.get_standard_json_serialization()
        hjs.enable_dynamic_nodes()
        serialized_chunk = hjs.serialize_tree_to_serialization_block(lang)

        self.assertEqual(5, len(serialized_chunk.get_classifier_instances()))
        serialized_l = serialized_chunk.get_classifier_instances()[0]
        self.assertEqual("l", serialized_l.get_id())
        self.assertIsNone(serialized_l.get_parent_node_id())

        serialized_c = serialized_chunk.get_instance_by_id("c")
        self.assertEqual("c", serialized_c.get_id())
        self.assertEqual(["metaAnn_1"], serialized_c.get_annotations())

        hjs.register_language(meta_lang)
        deserialized = hjs.deserialize_serialization_block(serialized_chunk)
        self.assertEqual(5, len(deserialized))

        self.assert_instances_are_equal(c, deserialized[3])
        self.assertEqual(deserialized[0], deserialized[3].get_parent())

        self.assert_instances_are_equal(ann, deserialized[4])
        self.assertEqual(deserialized[3], deserialized[4].get_parent())
        self.assertEqual(deserialized[3].get_annotations(), [deserialized[4]])

    def test_serialization_include_builtins_when_used_in_properties(self):
        lang = Language("l", "l", "l", "1")
        c = Concept(language=lang, name="c", id="c", key="c")
        c.add_feature(
            Property.create_required(name="foo", type=LionCoreBuiltins.get_string())
            .set_id("foo")
            .set_key("foo")
        )

        n1 = DynamicNode("n1", c)
        ClassifierInstanceUtils.set_property_value_by_name(n1, "foo", "abc")

        hjs = SerializationProvider.get_standard_json_serialization()
        serialized_chunk = hjs.serialize_nodes_to_serialization_block([n1])

        self.assertEqual(2, len(serialized_chunk.get_languages()))
        self.assertTrue(
            any(
                entry.get_key() == lang.get_key()
                and entry.get_version() == lang.get_version()
                for entry in serialized_chunk.get_languages()
            )
        )
        self.assertTrue(
            any(
                entry.get_key() == LionCoreBuiltins.get_instance().get_key()
                and entry.get_version() == LionCoreBuiltins.get_instance().get_version()
                for entry in serialized_chunk.get_languages()
            )
        )

    def test_deserialize_partial_tree_fails_by_default(self):
        js = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        language_is = open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "propertiesLanguage.json",
            "r",
        )
        properties_language = js.deserialize_json_to_nodes(json.load(language_is))[0]
        js.register_language(properties_language)
        is_ = open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "partialTree.json",
            "r",
        )

        js.enable_dynamic_nodes()
        with self.assertRaises(DeserializationException):
            js.deserialize_json_to_nodes(json.load(is_))

    def test_deserialize_partial_tree_succeeds_with_null_references_policy(self):
        js = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        language_is = open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "propertiesLanguage.json",
            "r",
        )
        properties_language = js.deserialize_json_to_nodes(json.load(language_is))[0]
        js.register_language(properties_language)
        is_ = open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "partialTree.json",
            "r",
        )

        js.enable_dynamic_nodes()
        js.unavailable_parent_policy = UnavailableNodePolicy.NULL_REFERENCES
        nodes = js.deserialize_json_to_nodes(json.load(is_))
        self.assertEqual(4, len(nodes))

    def test_deserialize_partial_tree_succeeds_with_proxy_nodes_policy(self):
        js = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        language_is = open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "propertiesLanguage.json",
            "r",
        )
        properties_language = js.deserialize_json_to_nodes(json.load(language_is))[0]
        js.register_language(properties_language)
        is_ = open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "partialTree.json",
            "r",
        )

        js.enable_dynamic_nodes()
        js.unavailable_parent_policy = UnavailableNodePolicy.PROXY_NODES
        nodes = js.deserialize_json_to_nodes(json.load(is_))
        self.assertEqual(5, len(nodes))

        pp1 = next(n for n in nodes if n.get_id() == "pp1")
        self.assertIsInstance(pp1, ProxyNode)

        pf1 = next(n for n in nodes if n.get_id() == "pf1")
        self.assertFalse(isinstance(pf1, ProxyNode))
        self.assertEqual(pp1, pf1.get_parent())

        self.assertTrue(all(not isinstance(n, ProxyNode) for n in nodes if n != pp1))

    def test_deserialize_tree_with_external_references_throw_error_policy(self):
        js = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        language_is = open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "todosLanguage.json",
            "r",
        )
        todos_language = js.deserialize_json_to_nodes(json.load(language_is))[0]
        js.register_language(todos_language)
        is_ = open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "todosWithExternalReferences.json",
            "r",
        )

        js.enable_dynamic_nodes()
        js.unavailable_parent_policy = UnavailableNodePolicy.NULL_REFERENCES
        js.unavailable_reference_target_policy = UnavailableNodePolicy.THROW_ERROR

        with self.assertRaises(DeserializationException):
            js.deserialize_json_to_nodes(json.load(is_))

    def test_deserialize_tree_with_external_references_proxy_nodes_policy(self):
        js = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        language_is = open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "todosLanguage.json",
            "r",
        )
        todos_language = js.deserialize_json_to_nodes(json.load(language_is))[0]
        js.register_language(todos_language)
        is_ = open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "todosWithExternalReferences.json",
            "r",
        )

        js.enable_dynamic_nodes()
        js.unavailable_parent_policy = UnavailableNodePolicy.NULL_REFERENCES
        js.unavailable_reference_target_policy = UnavailableNodePolicy.PROXY_NODES
        nodes = js.deserialize_json_to_nodes(json.load(is_))
        self.assertEqual(5, len(nodes))

        pr0td1 = next(
            n
            for n in nodes
            if n.get_id() == "synthetic_my-wonderful-partition_projects_0_todos_1"
        )
        self.assertIsInstance(pr0td1, ProxyNode)

        pr1td0 = next(
            n
            for n in nodes
            if n.get_id() == "synthetic_my-wonderful-partition_projects_1_todos_0"
        )
        self.assertIsInstance(pr1td0, DynamicNode)

    def test_deserialize_tree_with_external_references_null_policy(self):
        js = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        language_is = open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "todosLanguage.json",
            "r",
        )
        todos_language = js.deserialize_json_to_nodes(json.load(language_is))[0]
        js.register_language(todos_language)
        is_ = open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "todosWithExternalReferences.json",
            "r",
        )

        js.enable_dynamic_nodes()
        js.unavailable_parent_policy = UnavailableNodePolicy.NULL_REFERENCES
        js.unavailable_reference_target_policy = UnavailableNodePolicy.NULL_REFERENCES
        nodes = js.deserialize_json_to_nodes(json.load(is_))
        self.assertEqual(4, len(nodes))

    def test_deserialize_trees_with_children_not_provided(self):
        js = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        language_is = open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "todosLanguage.json",
            "r",
        )
        todos_language = js.deserialize_json_to_nodes(json.load(language_is))[0]
        js.register_language(todos_language)

        js.enable_dynamic_nodes()
        js.unavailable_parent_policy = UnavailableNodePolicy.NULL_REFERENCES
        js.unavailable_reference_target_policy = UnavailableNodePolicy.NULL_REFERENCES

        with self.assertRaises(UnresolvedClassifierInstanceException):
            is_ = open(
                Path(__file__).parent.parent
                / "resources"
                / "serialization"
                / "todosWithChildrenNotProvided.json",
                "r",
            )
            js.deserialize_json_to_nodes(json.load(is_))

    def test_deserialize_multiple_references_to_proxied_node(self):
        js = SerializationProvider.get_standard_json_serialization(
            LionWebVersion.V2023_1
        )
        language_is = open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "todosLanguage.json",
            "r",
        )
        todos_language = js.deserialize_json_to_nodes(json.load(language_is))[0]
        js.register_language(todos_language)

        js.enable_dynamic_nodes()
        js.unavailable_children_policy = UnavailableNodePolicy.PROXY_NODES
        js.unavailable_parent_policy = UnavailableNodePolicy.PROXY_NODES
        js.unavailable_reference_target_policy = UnavailableNodePolicy.PROXY_NODES
        is_ = open(
            Path(__file__).parent.parent
            / "resources"
            / "serialization"
            / "todosWithMultipleProxies.json",
            "r",
        )
        nodes = js.deserialize_json_to_nodes(json.load(is_))

        self.assertEqual(5, len(nodes))
        todo0 = nodes[0]
        self.assertEqual(
            ProxyNode("synthetic_my-wonderful-partition_projects_1"), todo0.get_parent()
        )
        prerequisite_todo0 = ClassifierInstanceUtils.get_reference_value_by_name(
            todo0, "prerequisite"
        )
        self.assertEqual(
            [ReferenceValue(referred=ProxyNode("external-1"), resolve_info=None)],
            prerequisite_todo0,
        )


if __name__ == "__main__":
    unittest.main()
