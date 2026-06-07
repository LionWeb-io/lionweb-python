from lionweb.language.lioncore_builtins import LionCoreBuiltins
from lionweb.lionweb_version import LionWebVersion
from lionweb.serialization.json_serialization import JsonSerialization
from lionweb.serialization.protobuf_serialization import ProtoBufSerialization


def create_standard_json_serialization(
    lion_web_version: LionWebVersion = LionWebVersion.current_version(),
) -> JsonSerialization:
    """Create a :class:`JsonSerialization` set up with the standard LionWeb languages.

    Args:
        lion_web_version: The LionWeb version to target.

    Returns:
        A :class:`JsonSerialization` instance, initialized with LionCore and
        LionCoreBuiltins so that standard languages can be (de)serialized.

    Raises:
        ValueError: If ``lion_web_version`` is not a :class:`LionWebVersion`.
    """
    if lion_web_version is None:
        lion_web_version = LionWebVersion.current_version
    if not isinstance(lion_web_version, LionWebVersion):
        raise ValueError()
    serialization = JsonSerialization(lion_web_version)
    setup_standard_initialization(serialization)
    return serialization


def create_standard_protobuf_serialization(
    lion_web_version: LionWebVersion = LionWebVersion.current_version(),
) -> ProtoBufSerialization:
    """Create a :class:`ProtoBufSerialization` set up with the standard LionWeb languages.

    Args:
        lion_web_version: The LionWeb version to target.

    Returns:
        A :class:`ProtoBufSerialization` instance, initialized with LionCore and
        LionCoreBuiltins so that standard languages can be (de)serialized.

    Raises:
        ValueError: If ``lion_web_version`` is not a :class:`LionWebVersion`.
    """
    if lion_web_version is None:
        lion_web_version = LionWebVersion.current_version
    if not isinstance(lion_web_version, LionWebVersion):
        raise ValueError()
    serialization = ProtoBufSerialization(lion_web_version)
    setup_standard_initialization(serialization)
    return serialization


def setup_standard_initialization(serialization) -> None:
    """Register LionCore and LionCoreBuiltins languages and deserializers on a serialization.

    Args:
        serialization: The serialization instance (JSON or protobuf) to initialize.
    """
    from lionweb.self.lioncore import LionCore

    serialization.classifier_resolver.register_language(
        LionCore.get_instance(serialization.lion_web_version)
    )
    serialization.instantiator.register_lioncore_custom_deserializers(
        serialization.lion_web_version
    )
    serialization.primitive_values_serialization.register_lion_builtins_primitive_serializers_and_deserializers(
        serialization.lion_web_version
    )
    serialization.instance_resolver.extend(
        LionCore.get_instance(serialization.lion_web_version).this_and_all_descendants()
    )
    serialization.instance_resolver.extend(
        LionCoreBuiltins.get_instance(serialization.lion_web_version).this_and_all_descendants()
    )
