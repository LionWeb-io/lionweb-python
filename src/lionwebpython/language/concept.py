from typing import List, Optional, cast

from lionwebpython.language.classifier import Classifier
from lionwebpython.language.feature import Feature
from lionwebpython.language.interface import Interface
from lionwebpython.language.language import Language
from lionwebpython.lionweb_version import LionWebVersion
from lionwebpython.model.classifier_instance_utils import \
    ClassifierInstanceUtils
from lionwebpython.self.lioncore import LionCore


class Concept(Classifier["Concept"]):
    def __init__(
        self,
        lion_web_version: Optional[LionWebVersion] = None,
        language: Optional[Language] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
        key: Optional[str] = None,
    ):
        (
            super().__init__(lion_web_version, language, name, id)
            if lion_web_version
            else super().__init__(language=language, name=name, id=id)
        )
        self.set_abstract(False)
        self.set_partition(False)
        if key:
            self.set_key(key)

    def direct_ancestors(self) -> List[Classifier]:
        direct_ancestors: List[Classifier] = []
        extended = self.get_extended_concept()
        if extended:
            direct_ancestors.append(extended)
        direct_ancestors.extend(self.get_implemented())
        return direct_ancestors

    def is_abstract(self) -> bool:
        return cast(
            bool, self.get_property_value(property_name="abstract", default_value=False)
        )

    def set_abstract(self, value: bool):
        self.set_property_value(property_name="abstract", value=value)

    def is_partition(self) -> bool:
        return cast(
            bool,
            self.get_property_value(property_name="partition", default_value=False),
        )

    def set_partition(self, value: bool):
        self.set_property_value(property_name="partition", value=value)

    def get_extended_concept(self) -> Optional["Concept"]:
        return cast(Optional["Concept"], self.get_reference_single_value("extends"))

    def get_implemented(self) -> List[Interface]:
        return cast(List[Interface], self.get_reference_multiple_value("implements"))

    def add_implemented_interface(self, iface: Interface):
        self.add_reference_multiple_value(
            "implements", ClassifierInstanceUtils.reference_to(iface)
        )

    def set_extended_concept(self, extended: Optional["Concept"]):
        if extended is None:
            self.set_reference_single_value("extends", None)
        else:
            self.set_reference_single_value(
                "extends", ClassifierInstanceUtils.reference_to(extended)
            )

    def inherited_features(self) -> List[Feature]:
        result: List[Feature] = []
        for ancestor in self.all_ancestors():
            self.combine_features(result, ancestor.get_features())
        return result

    def get_classifier(self) -> "Concept":
        return LionCore.get_concept(self.get_lion_web_version())
