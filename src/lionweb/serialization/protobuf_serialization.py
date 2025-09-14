from typing import TYPE_CHECKING, Dict, List, Optional, Set

from lionweb.lionweb_version import LionWebVersion
from lionweb.serialization.data import LanguageVersion
from lionweb.serialization.data.serialized_reference_value import \
    SerializedReferenceValueEntry
from lionweb.serialization.deserialization_exception import \
    DeserializationException
from lionweb.serialization.proto import (PBChunk, PBContainment, PBLanguage,
                                         PBMetaPointer, PBNode, PBProperty,
                                         PBReference, PBReferenceValue)

from ..model import ClassifierInstance
from ..model.impl.proxy_node import ProxyNode
from .abstract_serialization import AbstractSerialization

if TYPE_CHECKING:
    from lionweb.serialization import (AbstractSerialization, MetaPointer,
                                       SerializationChunk,
                                       SerializedClassifierInstance)


class ProtoBufSerialization(AbstractSerialization):

    def __init__(
        self, lionweb_version: LionWebVersion = LionWebVersion.current_version()
    ) -> None:
        super().__init__(lionweb_version=lionweb_version)
        self._chunk_instance = PBChunk()  # Reusable instance

    def _read_pbchunk_from_bytes(self, data: bytes) -> PBChunk:
        """Read a protobuf Chunk from binary content"""
        self._chunk_instance.Clear()  # Reset the instance
        self._chunk_instance.ParseFromString(data)
        return self._chunk_instance

    def deserialize_chunk_from_bytes(self, data: bytes) -> "SerializationChunk":
        return self._deserialize_pbchunk_to_serialization_chunk(
            self._read_pbchunk_from_bytes(data)
        )

    def _deserialize_pbchunk_to_serialization_chunk(
        self, chunk: PBChunk
    ) -> "SerializationChunk":
        # Pre-size arrays
        string_count = len(chunk.interned_strings)
        language_count = len(chunk.interned_languages)
        meta_pointer_count = len(chunk.interned_meta_pointers)

        strings_array: List[Optional[str]] = [None] * (string_count + 1)
        strings_array[0] = None
        for i, s in enumerate(chunk.interned_strings):
            strings_array[i + 1] = s

        languages_array: List[Optional[LanguageVersion]] = [None] * (language_count + 1)
        languages_array[0] = None
        for i, language in enumerate(chunk.interned_languages):
            key = strings_array[language.si_key]
            version = strings_array[language.si_version]
            lv = LanguageVersion(key, version)
            languages_array[i + 1] = lv

        from .data.metapointer import MetaPointer
        from .data.serialized_chunk import SerializationChunk
        from .data.serialized_classifier_instance import \
            SerializedClassifierInstance
        from .data.serialized_containment_value import \
            SerializedContainmentValue
        from .data.serialized_property_value import SerializedPropertyValue
        from .data.serialized_reference_value import SerializedReferenceValue

        metapointers_array: List[MetaPointer] = [None] * meta_pointer_count  # type: ignore
        for i, mp in enumerate(chunk.interned_meta_pointers):
            if mp.li_language >= len(languages_array):
                raise DeserializationException(
                    f"Unable to deserialize meta pointer with language {mp.li_language}"
                )
            language_version = languages_array[mp.li_language]
            language_key: Optional[str] = (
                language_version.key if language_version is not None else None
            )
            language_v: Optional[str] = (
                language_version.version if language_version is not None else None
            )
            language_version = LanguageVersion(language_key, language_v)
            meta_pointer = MetaPointer(language_version, strings_array[mp.si_key])
            metapointers_array[i] = meta_pointer

        serialization_chunk = SerializationChunk()
        serialization_chunk.serialization_format_version = (
            chunk.serialization_format_version
        )

        valid_languages = [lv for lv in languages_array if lv is not None]
        for lv in valid_languages:
            serialization_chunk.add_language(lv)

        # Nodes
        for n in chunk.nodes:

            id = strings_array[n.si_id] if n.HasField("si_id") else None
            parent_node_id = (
                strings_array[n.si_parent] if n.HasField("si_parent") else None
            )
            classifier = metapointers_array[n.mpi_classifier]
            sci = SerializedClassifierInstance(
                id, classifier, parent_node_id=parent_node_id
            )

            # properties
            for p in n.properties:
                spv = SerializedPropertyValue(
                    metapointers_array[p.mpi_meta_pointer],
                    strings_array[p.si_value] if p.HasField("si_value") else None,
                )
                sci.add_property_value(spv)

            # containments
            for c in n.containments:
                children: List[Optional[str]] = []
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

                    reference = (
                        strings_array[rv.si_referred]
                        if rv.HasField("si_referred")
                        else None
                    )
                    resolve_info = (
                        strings_array[rv.si_resolveInfo]
                        if rv.HasField("si_resolveInfo")
                        else None
                    )
                    entry = SerializedReferenceValueEntry(resolve_info, reference)
                    srv.add_value(entry)
                if srv.value:
                    sci.add_reference_value(srv)

            for a in n.si_annotations:
                sci.add_annotation(strings_array[a])

            serialization_chunk.add_classifier_instance(sci)

        return serialization_chunk

    def serialize_chunk_to_bytes(
        self, serialization_chunk: "SerializationChunk"
    ) -> bytes:
        pb_chunk = self._serialize(serialization_chunk)
        return pb_chunk.SerializeToString()

    class _SerializeHelper:

        def __init__(self) -> None:
            self.meta_pointers: List[MetaPointer] = []
            self.strings: List[Optional[str]] = [None]
            self.languages: List[Optional[LanguageVersion]] = [None]

            self._meta_pointer_index: Dict[MetaPointer, int] = {}
            self._string_index: Dict[Optional[str], int] = {None: 0}
            self._language_index: Dict[Optional[LanguageVersion], int] = {None: 0}

        def string_indexer(self, s: Optional[str]) -> int:
            if s in self._string_index:
                return self._string_index[s]
            idx = len(self.strings)
            self.strings.append(s)
            self._string_index[s] = idx
            return idx

        def language_indexer(self, lang: Optional[LanguageVersion]) -> int:
            if lang in self._language_index:
                return self._language_index[lang]
            idx = len(self.languages)
            self.languages.append(lang)
            self._language_index[lang] = idx
            return idx

        def meta_pointer_indexer(self, mp: "MetaPointer") -> int:
            if mp in self._meta_pointer_index:
                return self._meta_pointer_index[mp]
            idx = len(self.meta_pointers)
            # ensure indices for subparts
            self.language_indexer(mp.language_version)
            self.string_indexer(mp.key)
            self.meta_pointers.append(mp)
            self._meta_pointer_index[mp] = idx
            return idx

        def serialize_node(self, n: "SerializedClassifierInstance") -> PBNode:
            b = PBNode()

            if n.id is not None:
                b.si_id = self.string_indexer(n.id)
            if n.parent_node_id is not None:
                b.si_parent = self.string_indexer(n.parent_node_id)

            b.mpi_classifier = self.meta_pointer_indexer(n.classifier)

            # properties
            for p in n.properties:
                pbp = PBProperty()
                if p.value is not None:
                    pbp.si_value = self.string_indexer(p.value)
                pbp.mpi_meta_pointer = self.meta_pointer_indexer(p.meta_pointer)
                b.properties.append(pbp)

            # containments
            for c in n.containments:
                pbc = PBContainment()
                pbc.si_children.extend(
                    self.string_indexer(cid) for cid in c.children_ids
                )
                pbc.mpi_meta_pointer = self.meta_pointer_indexer(c.meta_pointer)
                b.containments.append(pbc)

            # references
            for r in n.references:
                pbr = PBReference()
                for rv in r.value:
                    pbv = PBReferenceValue()
                    if rv.reference is not None:
                        pbv.si_referred = self.string_indexer(rv.reference)
                    if rv.resolve_info is not None:
                        pbv.si_resolveInfo = self.string_indexer(rv.resolve_info)
                    pbr.values.append(pbv)
                pbr.mpi_meta_pointer = self.meta_pointer_indexer(r.meta_pointer)
                b.references.append(pbr)

            # annotations
            for a in n.annotations:
                b.si_annotations.append(self.string_indexer(a))

            return b

    def serialize_tree(self, classifier_instance: ClassifierInstance) -> PBChunk:
        if isinstance(classifier_instance, ProxyNode):
            raise ValueError("Proxy nodes cannot be serialized")
        classifier_instances: "set[ClassifierInstance]" = set()
        ClassifierInstance.collect_self_and_descendants(
            classifier_instance, True, classifier_instances
        )
        filtered = [n for n in classifier_instances if not isinstance(n, ProxyNode)]
        sc = self.serialize_nodes_to_serialization_chunk(filtered)
        return self._serialize(sc)

    def _serialize(self, serialization_chunk: "SerializationChunk") -> PBChunk:
        chunk = PBChunk()
        chunk.serialization_format_version = (
            serialization_chunk.serialization_format_version
        )

        helper = self._SerializeHelper()

        instances: List[SerializedClassifierInstance] = (
            serialization_chunk.get_classifier_instances()
        )
        for inst in instances:
            chunk.nodes.append(helper.serialize_node(inst))

        # languages first (match Java’s ordering)
        for lv in helper.languages:
            if lv is not None:
                pl = PBLanguage()
                if lv.key is not None:
                    pl.si_key = helper.string_indexer(lv.key)
                if lv.version is not None:
                    pl.si_version = helper.string_indexer(lv.version)
                chunk.interned_languages.append(pl)

        for s in helper.strings:
            if s is not None:
                chunk.interned_strings.append(s)

        for mp in helper.meta_pointers:
            pmp = PBMetaPointer()
            pmp.li_language = helper.language_indexer(mp.language_version)
            if mp.key is not None:
                pmp.si_key = helper.string_indexer(mp.key)
            chunk.interned_meta_pointers.append(pmp)

        return chunk

    def serialize_nodes_to_bytes(
        self, classifier_instances: List[ClassifierInstance] | ClassifierInstance
    ) -> bytes:
        if isinstance(classifier_instances, ClassifierInstance):
            classifier_instances = [classifier_instances]
        chunk = self.serialize_nodes_to_serialization_chunk(classifier_instances)
        return self.serialize_chunk_to_bytes(chunk)

    def serialize_trees_to_bytes(self, roots: List[ClassifierInstance]) -> bytes:
        from lionweb.model.impl.proxy_node import ProxyNode

        nodes_ids: Set[str] = set()
        all_nodes: List[ClassifierInstance] = []

        for root in roots:
            classifier_instances: List[ClassifierInstance] = list()
            ClassifierInstance.collect_self_and_descendants(
                root, True, classifier_instances
            )

            for node in classifier_instances:
                id = node.id
                if not id:
                    raise ValueError()
                # We support serialization of incorrect nodes, so we allow nodes without an ID
                if id is not None:
                    if id not in nodes_ids:
                        all_nodes.append(node)
                        nodes_ids.add(id)
                else:
                    all_nodes.append(node)

        # Filter out ProxyNode instances before serialization
        filtered_nodes = [node for node in all_nodes if not isinstance(node, ProxyNode)]
        return self.serialize_nodes_to_bytes(filtered_nodes)

    def deserialize_bytes_to_nodes(self, data: bytes) -> List[ClassifierInstance]:
        chunk = self.deserialize_chunk_from_bytes(data)
        return self.deserialize_serialization_chunk(chunk)
