from typing import Optional

from lionwebpython.language.classifier import Classifier
from lionwebpython.language.concept import Concept
from lionwebpython.language.data_type import DataType
from lionwebpython.language.feature import Feature
from lionwebpython.lionweb_version import LionWebVersion


class Property(Feature):

    def __init__(
        self,
        lion_web_version: LionWebVersion,
        name: str,
        container: Classifier,
        id: str,
    ):
        raise ValueError("NOT TRANSLATED YET")

    @staticmethod
    def create_optional(
        lion_web_version: LionWebVersion, name: str, type: DataType
    ) -> "Property":
        raise ValueError("NOT TRANSLATED YET")

    @staticmethod
    def create_required(
        lion_web_version: LionWebVersion, name: str, type: DataType
    ) -> "Property":
        raise ValueError("NOT TRANSLATED YET")

    def get_type(self) -> Optional[DataType]:
        raise ValueError("NOT TRANSLATED YET")

    def set_type(self, type: DataType) -> "Property":
        raise ValueError("NOT TRANSLATED YET")

    def __str__(self) -> str:
        raise ValueError("NOT TRANSLATED YET")

    def get_classifier(self) -> Concept:
        raise ValueError("NOT TRANSLATED YET")
