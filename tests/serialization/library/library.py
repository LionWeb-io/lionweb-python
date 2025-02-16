from serialization.library.book import Book

from lionwebpython.language.concept import Concept
from lionwebpython.model.impl.dynamic_node import DynamicNode


class Library(DynamicNode):
    def __init__(self, id: str, name: str):
        from serialization.library.library_language import LibraryLanguage

        super().__init__(id, LibraryLanguage.LIBRARY)
        self.set_name(name)

    def get_classifier(self) -> Concept:
        from serialization.library.library_language import LibraryLanguage

        return LibraryLanguage.LIBRARY

    def add_book(self, book: Book):
        containment = self.get_classifier().get_containment_by_name("books")
        self.add_child(containment, book)

    def set_name(self, name: str):
        property_ = self.get_classifier().get_property_by_name("name")
        self.set_property_value(property=property_, value=name)
