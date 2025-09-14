import unittest
from enum import Enum

from lionweb.language import Annotation, Concept, Language, Property
from lionweb.language.lioncore_builtins import LionCoreBuiltins
from lionweb.model.impl.dynamic_annotation_instance import \
    DynamicAnnotationInstance
from lionweb.model.impl.dynamic_node import DynamicNode
from lionweb.serialization import create_standard_protobuf_serialization
from lionweb.serialization.data import LanguageVersion
from lionweb.serialization.data.metapointer import MetaPointer
from lionweb.serialization.deserialization_exception import \
    DeserializationException
from lionweb.serialization.protobuf_serialization import ProtoBufSerialization

from .refsmm.container_node import ContainerNode
from .refsmm.ref_node import RefNode
from .refsmm.refs_language import RefsLanguage
from .serialization_test import SerializationTest
from .simplemath.int_literal import IntLiteral
from .simplemath.simple_math_language import SimpleMathLanguage
from .simplemath.sum import Sum


class MyEnum(Enum):
    el1 = "el1"
    el2 = "el2"


class ProtobufSerializationTest(SerializationTest):

    def _prepare_deserialization_of_simple_math(
        self, protobuf_serialization: ProtoBufSerialization
    ):
        protobuf_serialization.classifier_resolver.register_language(
            SimpleMathLanguage.INSTANCE
        )

        # Register custom deserializer for IntLiteral
        def deserialize_int_literal(
            concept, serialized_node, deserialized_nodes_by_id, properties_values
        ):
            value = properties_values.get(concept.get_property_by_name("value"))
            return IntLiteral(value, serialized_node.id)

        protobuf_serialization.instantiator.register_custom_deserializer(
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
            left = deserialized_nodes_by_id.get(left_scv.children_ids[0])

            right_scv = next(
                c
                for c in serialized_node.containments
                if c.meta_pointer.key == "SimpleMath_Sum_right"
            )
            right = deserialized_nodes_by_id.get(right_scv.children_ids[0])

            return Sum(left, right, serialized_node.id)

        protobuf_serialization.instantiator.register_custom_deserializer(
            SimpleMathLanguage.SUM.id, deserialize_sum
        )

    def test_deserialize_multiple_roots(self):
        sum1 = Sum(IntLiteral(1), IntLiteral(2))
        sum2 = Sum(IntLiteral(3), IntLiteral(4))
        pb = create_standard_protobuf_serialization()
        serialized = pb.serialize_trees_to_bytes([sum1, sum2])

        self._prepare_deserialization_of_simple_math(pb)
        deserialized = [
            n for n in pb.deserialize_bytes_to_nodes(serialized) if isinstance(n, Sum)
        ]
        self.assertEqual(deserialized, [sum1, sum2])

    def test_deserialize_nodes_without_ids_in_the_right_order(self):
        il1 = IntLiteral(1, None)
        il2 = IntLiteral(2, None)
        il3 = IntLiteral(3, None)
        il4 = IntLiteral(4, None)
        pb = create_standard_protobuf_serialization()
        serialized = pb.serialize_trees_to_bytes([il1, il2, il3, il4])

        self._prepare_deserialization_of_simple_math(pb)
        deserialized = [node for node in pb.deserialize_bytes_to_nodes(serialized)]
        self.assertEqual(deserialized, [il1, il2, il3, il4])

    def test_deserialize_trees_without_ids_in_the_right_order(self):
        il1 = IntLiteral(1, "int_1")
        il2 = IntLiteral(2, "int_2")
        sum1 = Sum(il1, il2, None)
        il3 = IntLiteral(3, "int_3")
        il4 = IntLiteral(4, "int_4")
        sum2 = Sum(il3, il4, None)
        pb = create_standard_protobuf_serialization()

        serialized = pb.serialize_trees_to_bytes([sum1, sum2])
        self._prepare_deserialization_of_simple_math(pb)
        deserialized = pb.deserialize_bytes_to_nodes(serialized)

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

        pb = create_standard_protobuf_serialization()
        serialized = pb.serialize_nodes_to_bytes([il4, il1, sum1, il2, sum2, il3])
        self._prepare_deserialization_of_simple_math(pb)
        deserialized = pb.deserialize_bytes_to_nodes(serialized)

        self.assertEqual(deserialized, [il4, il1, sum1, il2, sum2, il3])

    def test_deserialize_children_with_null_id(self):
        # Expecting DeserializationException
        il1 = IntLiteral(1, "int_1")
        il2 = IntLiteral(2, None)
        # Let's override it, as it gets a random id
        il2._id = None
        sum1 = Sum(il1, il2, None)

        pb = create_standard_protobuf_serialization()
        serialized = pb.serialize_nodes_to_bytes([sum1, il1, il2])
        self._prepare_deserialization_of_simple_math(pb)

        with self.assertRaises(DeserializationException):
            pb.deserialize_bytes_to_nodes(serialized)

    def prepare_deserialization_of_refmm(self, js):
        js.classifier_resolver.register_language(RefsLanguage.INSTANCE)
        js.instantiator.register_custom_deserializer(
            RefsLanguage.CONTAINER_NODE.id,
            lambda concept, serialized_node, deserialized_nodes_by_id, properties_values: ContainerNode(
                properties_values.get(concept.get_containment_by_name("contained")),
                serialized_node.id,
            ),
        )
        js.instantiator.register_custom_deserializer(
            RefsLanguage.REF_NODE.id,
            lambda concept, serialized_node, deserialized_nodes_by_id, properties_values: RefNode(
                serialized_node.id
            ),
        )

    def test_dead_references(self):
        r1 = RefNode()
        r2 = RefNode()
        r1.set_referred(r2)

        pb = create_standard_protobuf_serialization()
        serialized = pb.serialize_nodes_to_bytes([r1])
        self.prepare_deserialization_of_refmm(pb)

        with self.assertRaises(DeserializationException):
            pb.deserialize_bytes_to_nodes(serialized)

    def test_references_loop(self):
        r1 = RefNode()
        r2 = RefNode()
        r3 = RefNode()
        r1.set_referred(r2)
        r2.set_referred(r3)
        r3.set_referred(r1)

        pb = create_standard_protobuf_serialization()
        serialized = pb.serialize_nodes_to_bytes([r1, r2, r3])
        self.prepare_deserialization_of_refmm(pb)
        deserialized = pb.deserialize_bytes_to_nodes(serialized)

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
        from lionweb.model.classifier_instance_utils import get_children

        self.assertEqual(get_children(c1), [c2])
        self.assertEqual(get_children(c2), [c1])

        pb = create_standard_protobuf_serialization()
        serialized = pb.serialize_nodes_to_bytes([c1, c2])
        self.prepare_deserialization_of_refmm(pb)

        with self.assertRaises(DeserializationException):
            pb.deserialize_bytes_to_nodes(serialized)

    def test_serialization_of_language_versions_with_imports(self):
        my_language = Language()
        my_language.set_key("myLanguage-key")
        my_language.set_version("3")

        my_concept = Concept()
        my_concept.add_implemented_interface(LionCoreBuiltins.get_inamed())
        my_language.add_element(my_concept)

        my_instance = DynamicNode("instance-a", my_concept)
        json_ser = create_standard_protobuf_serialization()
        json_ser.keep_null_properties = True
        serialized_chunk = json_ser.serialize_nodes_to_serialization_chunk(
            [my_instance]
        )

        self.assertEqual(1, len(serialized_chunk.get_classifier_instances()))
        serialized_classifier_instance = serialized_chunk.get_classifier_instances()[0]
        self.assertEqual("instance-a", serialized_classifier_instance.id)
        self.assertEqual(1, len(serialized_classifier_instance.properties))
        serialized_name = serialized_classifier_instance.properties[0]
        expected_pointer = MetaPointer(
            LanguageVersion("LionCore-builtins", "2024.1"),
            "LionCore-builtins-INamed-name",
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

        hjs = create_standard_protobuf_serialization()
        hjs.enable_dynamic_nodes()
        serialized_chunk = hjs.serialize_nodes_to_serialization_chunk([n1])

        self.assertEqual(4, len(serialized_chunk.get_classifier_instances()))
        serialized_n1 = serialized_chunk.get_classifier_instances()[0]
        self.assertEqual("n1", serialized_n1.id)
        self.assertIsNone(serialized_n1.get_parent_node_id())
        self.assertEqual(["a1_1", "a1_2", "a2_3"], serialized_n1.annotations)

        deserialized = hjs.deserialize_serialization_chunk(serialized_chunk)
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

        hjs = create_standard_protobuf_serialization()
        hjs.enable_dynamic_nodes()
        serialized_chunk = hjs.serialize_tree_to_serialization_chunk(lang)

        self.assertEqual(5, len(serialized_chunk.get_classifier_instances()))
        serialized_l = serialized_chunk.get_classifier_instances()[0]
        self.assertEqual("l", serialized_l.id)
        self.assertIsNone(serialized_l.get_parent_node_id())

        serialized_c = serialized_chunk.get_instance_by_id("c")
        self.assertEqual("c", serialized_c.id)
        self.assertEqual(["metaAnn_1"], serialized_c.annotations)

        hjs.register_language(meta_lang)
        deserialized = hjs.deserialize_serialization_chunk(serialized_chunk)
        self.assertEqual(5, len(deserialized))

        self.assert_instances_are_equal(c, deserialized[3])
        self.assertEqual(deserialized[0], deserialized[3].get_parent())

        self.assert_instances_are_equal(ann, deserialized[4])
        self.assertEqual(deserialized[3], deserialized[4].get_parent())
        self.assertEqual(deserialized[3].annotations, [deserialized[4]])

    def test_serialization_include_builtins_when_used_in_properties(self):
        lang = Language("l", "l", "l", "1")
        c = Concept(language=lang, name="c", id="c", key="c")
        c.add_feature(
            Property.create_required(name="foo", type=LionCoreBuiltins.get_string())
            .set_id("foo")
            .set_key("foo")
        )

        n1 = DynamicNode("n1", c)
        from lionweb.model.classifier_instance_utils import \
            set_property_value_by_name

        set_property_value_by_name(n1, "foo", "abc")

        hjs = create_standard_protobuf_serialization()
        serialized_chunk = hjs.serialize_nodes_to_serialization_chunk([n1])

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


if __name__ == "__main__":
    unittest.main()
