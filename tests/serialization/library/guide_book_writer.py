from serialization.library.writer import Writer

from lionwebpython.language.concept import Concept


class GuideBookWriter(Writer):
    def __init__(self, id: str, name: str):
        from serialization.library.library_language import LibraryLanguage

        super().__init__(id, name, LibraryLanguage.GUIDE_BOOK_WRITER)

    def set_countries(self, countries: str):
        property_ = self.get_classifier().get_property_by_name("countries")
        self.set_property_value(property=property_, value=countries)

    def get_classifier(self) -> Concept:
        from serialization.library.library_language import LibraryLanguage

        return LibraryLanguage.GUIDE_BOOK_WRITER
