from dataclasses import dataclass

from lionweb import LionWebVersion
from lionweb.language import Containment
from lionweb.model import ClassifierInstance
from lionweb.serialization import (
    JsonSerialization,
    MetaPointer,
    SerializedClassifierInstance,
    create_standard_json_serialization,
)


class BulkImport:
    """Accumulates serialized nodes and attach points for a bulk-import request.

    Nodes can be added either as already-serialized `SerializedClassifierInstance`
    objects, or as live `ClassifierInstance` objects (which get serialized
    immediately). Attach points describe where imported subtrees should be
    grafted onto an existing repository.
    """

    # Cache for JsonSerialization per LionWebVersion
    _json_serializations: dict[LionWebVersion, JsonSerialization] = {}

    @staticmethod
    def _get_json_serialization(lion_web_version: LionWebVersion) -> JsonSerialization:
        """Return cached JsonSerialization for a given LionWebVersion."""
        if lion_web_version not in BulkImport._json_serializations:
            BulkImport._json_serializations[lion_web_version] = create_standard_json_serialization(
                lion_web_version
            )
        return BulkImport._json_serializations[lion_web_version]

    def __init__(
        self,
        attach_points: list["BulkImport.AttachPoint"] | None = None,
        nodes: list[ClassifierInstance] | None = None,
    ) -> None:
        """
        If `nodes` is a list of ClassifierInstance, serialize them into
        SerializedClassifierInstance immediately (matching the Java behavior).
        """
        self._attach_points: list[BulkImport.AttachPoint] = attach_points or []
        self._nodes: list[SerializedClassifierInstance] = []

        nodes = nodes or []
        if nodes:
            json_serialization = self._get_json_serialization(
                nodes[0].get_classifier().get_lionweb_version()
            )
            serialized_chunk = json_serialization.serialize_nodes_to_serialization_chunk(nodes)
            self._nodes = list(serialized_chunk.get_classifier_instances())

    # --- mutation API ---

    def add_node(self, classifier_instance: ClassifierInstance) -> None:
        """Serialize the given ClassifierInstance and append all resulting serialized instances."""
        json_serialization = self._get_json_serialization(
            classifier_instance.get_classifier().get_lionweb_version()
        )
        serialized_chunk = json_serialization.serialize_nodes_to_serialization_chunk(
            classifier_instance
        )
        self._nodes.extend(serialized_chunk.get_classifier_instances())

    def add_nodes(self, classifier_instances: list[SerializedClassifierInstance]) -> None:
        """Append already-serialized classifier instances as-is."""
        self._nodes.extend(classifier_instances)

    def add_attach_point(self, attach_point: "BulkImport.AttachPoint") -> None:
        self._attach_points.append(attach_point)

    def clear(self) -> None:
        self._attach_points.clear()
        self._nodes.clear()

    # --- accessors ---

    def get_attach_points(self) -> list["BulkImport.AttachPoint"]:
        return self._attach_points

    def get_nodes(self) -> list[SerializedClassifierInstance]:
        return self._nodes

    def number_of_nodes(self) -> int:
        return len(self._nodes)

    def is_empty(self) -> bool:
        return len(self._nodes) == 0

    # --- dunder conveniences (optional) ---

    def __len__(self) -> int:
        return len(self._nodes)

    def __bool__(self) -> bool:
        return not self.is_empty()

    # --- nested class ---

    @dataclass
    class AttachPoint:
        """Describes where a set of imported nodes should be attached.

        Attributes:
            container: ID of the node that will contain the imported root.
            containment: The containment feature (as a MetaPointer) under which
                the imported root will be attached.
            root_id: ID of the root node being attached.
        """

        container: str
        containment: MetaPointer
        root_id: str

        @classmethod
        def from_meta(
            cls, container: str, containment: MetaPointer, root_id: str
        ) -> "BulkImport.AttachPoint":
            return cls(container=container, containment=containment, root_id=root_id)

        @classmethod
        def from_containment(
            cls, container: str, containment: Containment, root_id: str
        ) -> "BulkImport.AttachPoint":
            # Mirrors: MetaPointer.from(containment)
            mp = (
                MetaPointer.from_(containment)
                if hasattr(MetaPointer, "from_")
                else MetaPointer.from_feature(containment)
            )
            return cls(container=container, containment=mp, root_id=root_id)
