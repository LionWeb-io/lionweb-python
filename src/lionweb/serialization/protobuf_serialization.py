import io
from typing import List, Optional, Dict, TYPE_CHECKING

from zipp.compat.overlay import zipfile

from lionweb.lionweb_version import LionWebVersion
from lionweb.serialization import MetaPointer, SerializedClassifierInstance, SerializedPropertyValue, \
    SerializedContainmentValue, SerializedReferenceValue
from lionweb.serialization.data import LanguageVersion

import src.lionweb.serialization.proto.Chunk_pb2 as pb
from lionweb.serialization.data.serialized_reference_value import SerializedReferenceValueEntry
from lionweb.serialization.deserialization_exception import DeserializationException
from lionweb.serialization.data import SerializationChunk

if TYPE_CHECKING:

    from lionweb.model import Node
    from lionweb.serialization.data import SerializationChunk


# from io.lionweb.serialization.data import (
#     SerializationChunk,
#     SerializedClassifierInstance,
#     SerializedPropertyValue,
#     SerializedContainmentValue,
#     SerializedReferenceValue,
#     LanguageVersion,
# )
# from io.lionweb.serialization.data.meta_pointer import MetaPointer
# from io.lionweb.model import ClassifierInstance as LWClassifierInstance
# from io.lionweb.model.impl import ProxyNode
# from io.lionweb.serialization.exceptions import DeserializationException
# # ------------------------------------------------------------------


class ProtoBufSerialization:

    def __init__(self, lionweb_version: Optional["LionWebVersion"] = LionWebVersion.current_version()) -> None:
        self._lionweb_version = lionweb_version

    # # -------------------- Deserialization --------------------
    #
    # def deserialize_to_nodes_from_bytes(self, data: bytes) -> List[Node]:
    #     pb_chunk = pb.S(data)
    #     return self.deserialize_to_nodes_from_pbchunk(pb_chunk)
    #
    # def deserialize_to_chunk_from_bytes(self, data: bytes) -> SerializationChunk:
    #     pb_chunk = pb.FromString(data)
    #     return self._deserialize_serialization_chunk(pb_chunk)
    #
    # def deserialize_to_nodes_from_file(self, path: str) -> List[Node]:
    #     with open(path, "rb") as f:
    #         return self.deserialize_to_nodes_from_stream(f)
    #
    # def deserialize_to_nodes_from_stream(self, stream) -> List[Node]:
    #     data = stream.read()
    #     pb_chunk = pb.FromString(data)
    #     return self.deserialize_to_nodes_from_pbchunk(pb_chunk)
    #
    # def deserialize_to_nodes_from_pbchunk(self, chunk: PBChunk) -> List[Node]:
    #     cis = self.deserialize_to_classifier_instances_from_pbchunk(chunk)
    #     # Keep only Node instances
    #     return [ci for ci in cis if isinstance(ci, LWClassifierInstance.Node)]  # adjust if needed
    #
    # def deserialize_to_classifier_instances_from_pbchunk(
    #         self, chunk: PBChunk
    # ) -> List[LWClassifierInstance]:
    #     serialization_chunk = self._deserialize_serialization_chunk(chunk)
    #     self._validate_serialization_block(serialization_chunk)
    #     return self._deserialize_serialization_chunk_to_instances(serialization_chunk)
    #
    def _deserialize_pbchunk_to_serialization_chunk(self, chunk: pb.PBChunk) -> SerializationChunk:
        # Pre-size arrays as in Java
        string_count = len(chunk.interned_strings)
        language_count = len(chunk.interned_languages)
        meta_pointer_count = len(chunk.interned_meta_pointers)

        strings_array: List[Optional[str]] = [None] * (string_count + 1)
        strings_array[0] = None
        for i, s in enumerate(chunk.interned_strings):
            strings_array[i + 1] = s

        languages_array: List[Optional[LanguageVersion]] = [None] * (language_count + 1)
        languages_array[0] = None
        for i, l in enumerate(chunk.interned_languages):
            key = strings_array[l.si_key]
            version = strings_array[l.si_version]
            lv = LanguageVersion(key, version)
            languages_array[i + 1] = lv

        metapointers_array: List[MetaPointer] = [None] * meta_pointer_count  # type: ignore
        for i, mp in enumerate(chunk.interned_meta_pointers):
            if mp.li_language >= len(languages_array):
                raise DeserializationException(
                    f"Unable to deserialize meta pointer with language {mp.li_language}"
                )
            language_version = languages_array[mp.li_language]
            meta_pointer = MetaPointer(
                language_version.key, language_version.version, strings_array[mp.si_key]
            )
            metapointers_array[i] = meta_pointer

        serialization_chunk = SerializationChunk()
        serialization_chunk.serialization_format_version = chunk.serialization_format_version

        for lv in languages_array:
            if lv is not None:
                serialization_chunk.add_language(lv)

        # Nodes
        for n in chunk.nodes:

            id = strings_array[n.si_id] if n.HasField("si_id") else None
            parent_node_id = strings_array[n.si_parent] if n.HasField("si_parent") else None
            classifier = metapointers_array[n.mpi_classifier]
            sci = SerializedClassifierInstance(id, classifier, parent_node_id=parent_node_id)

            # properties
            for p in n.properties:
                spv = SerializedPropertyValue(
                    metapointers_array[p.mpi_meta_pointer],
                    strings_array[p.si_value] if p.HasField("si_value") else None,
                )
                sci.add_property_value(spv)

            # containments
            for c in n.containments:
                children: List[str] = []
                for child_index in c.si_children:
                    if child_index == 0:
                        raise DeserializationException(
                            "Unable to deserialize child identified by Null ID"
                        )
                    children.append(strings_array[child_index])
                if children:
                    scv = SerializedContainmentValue(
                        metapointers_array[c.mpi_meta_pointer], children
                    )
                    sci.add_containment_value(scv)

            # references
            for r in n.references:
                srv = SerializedReferenceValue(metapointers_array[r.mpi_meta_pointer])
                for rv in r.values:

                    reference = strings_array[rv.si_referred] if rv.HasField("si_referred") else None
                    resolve_info = strings_array[rv.si_resolveInfo] if rv.HasField("si_resolveInfo") else None
                    entry = SerializedReferenceValueEntry(resolve_info, reference)
                    srv.add_value(entry)
                if srv.value:
                    sci.add_reference_value(srv)

            for a in n.si_annotations:
                sci.add_annotation(strings_array[a])

            serialization_chunk.add_classifier_instance(sci)

        return serialization_chunk
    #
    # def _validate_serialization_block(self, serialization_chunk: SerializationChunk) -> None:
    #     # Mirror whatever the Java AbstractSerialization.validateSerializationBlock does.
    #     # If you have that logic elsewhere, call it here.
    #     pass
    #
    # def _deserialize_serialization_chunk_to_instances(
    #         self, serialization_chunk: SerializationChunk
    # ) -> List[LWClassifierInstance]:
    #     # In Java this likely transforms SerializedClassifierInstance -> runtime model instances.
    #     # If you already have a function for that, call it here. Placeholder:
    #     return serialization_chunk.get_classifier_instances()
    #
    # # -------------------- Serialization --------------------
    #
    # def serialize_trees_to_bytes(self, *roots: LWClassifierInstance) -> bytes:
    #     nodes_ids: set = set()
    #     all_nodes: List[LWClassifierInstance] = []
    #
    #     for root in roots:
    #         classifier_instances: "set[LWClassifierInstance]" = set()
    #         LWClassifierInstance.collectSelfAndDescendants(root, True, classifier_instances)
    #
    #         for n in classifier_instances:
    #             nid = getattr(n, "id", None)
    #             if nid is not None:
    #                 if nid not in nodes_ids:
    #                     all_nodes.append(n)
    #                     nodes_ids.add(nid)
    #             else:
    #                 all_nodes.append(n)
    #
    #     # Filter out ProxyNode
    #     filtered_nodes = [n for n in all_nodes if not isinstance(n, ProxyNode)]
    #     return self.serialize_nodes_to_bytes(filtered_nodes)
    #
    # def serialize_nodes_to_bytes(self, classifier_instances: List[LWClassifierInstance]) -> bytes:
    #     if any(isinstance(n, ProxyNode) for n in classifier_instances):
    #         raise ValueError("Proxy nodes cannot be serialized")
    #     serialization_block = self._serialize_nodes_to_serialization_chunk(classifier_instances)
    #     return self.serialize_to_bytes(serialization_block)
    #
    # def serialize_to_bytes(self, serialization_chunk: SerializationChunk) -> bytes:
    #     pb_chunk = self._serialize(serialization_chunk)
    #     return pb_chunk.SerializeToString()
    #
    # def _serialize_nodes_to_serialization_chunk(
    #         self, classifier_instances: List[LWClassifierInstance]
    # ) -> SerializationChunk:
    #     # Assuming you have equivalent functionality; call into your existing builder.
    #     # Placeholder: if you already store SerializedClassifierInstance in the chunk, pass through.
    #     sc = SerializationChunk()
    #     # NOTE: You likely have domain-specific logic to convert real model instances
    #     # into SerializedClassifierInstance; wire that here.
    #     raise NotImplementedError("Implement model -> SerializedClassifierInstance marshalling")
    #
    # class _SerializeHelper:
    #     """Mirror of the Java inner class SerializeHelper, adapted to Python."""
    #
    #     def __init__(self) -> None:
    #         self.meta_pointers: List[MetaPointer] = []
    #         self.strings: List[Optional[str]] = [None]
    #         self.languages: List[Optional[LanguageVersion]] = [None]
    #
    #         self._meta_pointer_index: Dict[MetaPointer, int] = {}
    #         self._string_index: Dict[Optional[str], int] = {None: 0}
    #         self._language_index: Dict[Optional[LanguageVersion], int] = {None: 0}
    #
    #     def string_indexer(self, s: Optional[str]) -> int:
    #         if s in self._string_index:
    #             return self._string_index[s]
    #         idx = len(self.strings)
    #         self.strings.append(s)
    #         self._string_index[s] = idx
    #         return idx
    #
    #     def language_indexer(self, l: Optional[LanguageVersion]) -> int:
    #         if l in self._language_index:
    #             return self._language_index[l]
    #         idx = len(self.languages)
    #         self.languages.append(l)
    #         self._language_index[l] = idx
    #         return idx
    #
    #     def meta_pointer_indexer(self, mp: MetaPointer) -> int:
    #         if mp in self._meta_pointer_index:
    #             return self._meta_pointer_index[mp]
    #         idx = len(self.meta_pointers)
    #         # ensure indices for subparts
    #         self.language_indexer(mp.language_version)
    #         self.string_indexer(mp.key)
    #         self.meta_pointers.append(mp)
    #         self._meta_pointer_index[mp] = idx
    #         return idx
    #
    #     def serialize_node(self, n: SerializedClassifierInstance) -> PBNode:
    #         b = PBNode()
    #
    #         if n.id is not None:
    #             b.si_id = self.string_indexer(n.id)
    #         if n.parent_node_id is not None:
    #             b.si_parent = self.string_indexer(n.parent_node_id)
    #
    #         b.mpi_classifier = self.meta_pointer_indexer(n.classifier)
    #
    #         # properties
    #         for p in n.properties:
    #             pbp = PBProperty()
    #             if p.value is not None:
    #                 pbp.si_value = self.string_indexer(p.value)
    #             pbp.mpi_meta_pointer = self.meta_pointer_indexer(p.meta_pointer)
    #             b.properties.append(pbp)
    #
    #         # containments
    #         for c in n.containments:
    #             pbc = PBContainment()
    #             pbc.si_children.extend(self.string_indexer(cid) for cid in c.children_ids)
    #             pbc.mpi_meta_pointer = self.meta_pointer_indexer(c.meta_pointer)
    #             b.containments.append(pbc)
    #
    #         # references
    #         for r in n.references:
    #             pbr = PBReference()
    #             for rv in r.value:
    #                 pbv = PBReferenceValue()
    #                 if rv.reference is not None:
    #                     pbv.si_referred = self.string_indexer(rv.reference)
    #                 if rv.resolve_info is not None:
    #                     pbv.si_resolve_info = self.string_indexer(rv.resolve_info)
    #                 pbr.values.append(pbv)
    #             pbr.mpi_meta_pointer = self.meta_pointer_indexer(r.meta_pointer)
    #             b.references.append(pbr)
    #
    #         # annotations
    #         for a in n.annotations:
    #             b.si_annotations.append(self.string_indexer(a))
    #
    #         return b
    #
    # def serialize_tree(self, classifier_instance: LWClassifierInstance) -> PBChunk:
    #     if isinstance(classifier_instance, ProxyNode):
    #         raise ValueError("Proxy nodes cannot be serialized")
    #     classifier_instances: "set[LWClassifierInstance]" = set()
    #     LWClassifierInstance.collectSelfAndDescendants(
    #         classifier_instance, True, classifier_instances
    #     )
    #     filtered = [n for n in classifier_instances if not isinstance(n, ProxyNode)]
    #     sc = self._serialize_nodes_to_serialization_chunk(filtered)
    #     return self._serialize(sc)
    #
    # def _serialize(self, serialization_chunk: SerializationChunk) -> PBChunk:
    #     chunk = PBChunk()
    #     chunk.serialization_format_version = serialization_chunk.serialization_format_version
    #
    #     helper = self._SerializeHelper()
    #
    #     instances: List[SerializedClassifierInstance] = serialization_chunk.get_classifier_instances()
    #     for inst in instances:
    #         chunk.nodes.append(helper.serialize_node(inst))
    #
    #     # languages first (match Java’s ordering)
    #     for lv in helper.languages:
    #         if lv is not None:
    #             pl = PBLanguage()
    #             if lv.key is not None:
    #                 pl.si_key = helper.string_indexer(lv.key)
    #             if lv.version is not None:
    #                 pl.si_version = helper.string_indexer(lv.version)
    #             chunk.interned_languages.append(pl)
    #
    #     for s in helper.strings:
    #         if s is not None:
    #             chunk.interned_strings.append(s)
    #
    #     for mp in helper.meta_pointers:
    #         pmp = PBMetaPointer()
    #         pmp.li_language = helper.language_indexer(mp.language_version)
    #         if mp.key is not None:
    #             pmp.si_key = helper.string_indexer(mp.key)
    #         chunk.interned_meta_pointers.append(pmp)
    #
    #     return chunk

if __name__ == "__main__":
    ps = ProtoBufSerialization(LionWebVersion.V2023_1)
    with zipfile.ZipFile(f, 'r') as zf:
        for name in zf.namelist():
            content = zf.read(name)   # bytes
            pb_chunk = pb.PBChunk()
            pb_chunk.ParseFromString(content)
            chunk = ps._deserialize_pbchunk_to_serialization_chunk(pb_chunk)
