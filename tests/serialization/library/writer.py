from typing import Optional, cast

from lionweb.language.concept import Concept
from lionweb.model.classifier_instance_utils import get_property_value_by_name
from lionweb.model.impl.dynamic_node import DynamicNode

from .library_language import LibraryLanguage


class Writer(DynamicNode):

    def __init__(self, id: str, name: Optional[str] = None):
        super().__init__(id=id, concept=LibraryLanguage.WRITER)
        if name is not None:
            self.set_name(name)

    def set_name(self, name: str) -> None:
        property = self.get_classifier().get_property_by_name("name")
        self.set_property_value(property=property, value=name)

    def get_name(self) -> str:
        return cast(str, get_property_value_by_name(self, "name"))

    def get_classifier(self) -> Concept:
        return LibraryLanguage.WRITER
