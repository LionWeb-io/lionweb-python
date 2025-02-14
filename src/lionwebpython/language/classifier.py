from lionwebpython.language.language_entity import LanguageEntity
from lionwebpython.language.namespace_provider import NamespaceProvider
from lionwebpython.lionweb_version import LionWebVersion


class Classifier(LanguageEntity, NamespaceProvider):
    def get_lion_web_version(self) -> LionWebVersion:
        raise ValueError("NOT YET TRANSLATED")
