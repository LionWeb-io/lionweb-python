from lionwebpython.language.lioncore_builtins import LionCoreBuiltins
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.serialization.json_serialization import JsonSerialization


class SerializationProvider:

    @staticmethod
    def get_standard_json_serialization(
        lion_web_version: LionWebVersion = LionWebVersion.current_version(),
    ):
        if lion_web_version is None:
            lion_web_version = LionWebVersion.current_version
        if not isinstance(lion_web_version, LionWebVersion):
            raise ValueError()
        serialization = JsonSerialization(lion_web_version)
        SerializationProvider.standard_initialization(serialization)
        return serialization

    @staticmethod
    def get_basic_json_serialization(
        lion_web_version: LionWebVersion = LionWebVersion.current_version(),
    ):
        if lion_web_version is None:
            return JsonSerialization()
        return JsonSerialization(lion_web_version)

    @staticmethod
    def standard_initialization(serialization):
        from lionwebpython.self.lioncore import LionCore

        serialization.classifier_resolver.register_language(
            LionCore.get_instance(serialization.lion_web_version)
        )
        serialization.instantiator.register_lioncore_custom_deserializers(
            serialization.lion_web_version
        )
        serialization.primitive_values_serialization.register_lion_builtins_primitive_serializers_and_deserializers(
            serialization.lion_web_version
        )
        serialization.instance_resolver.add_all(
            LionCore.get_instance(
                serialization.lion_web_version
            ).this_and_all_descendants()
        )
        serialization.instance_resolver.add_all(
            LionCoreBuiltins.get_instance(
                serialization.lion_web_version
            ).this_and_all_descendants()
        )
