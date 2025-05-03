from lionweb.language import Language, Concept
from lionweb.lionweb_version import LionWebVersion
from functools import lru_cache


@lru_cache(maxsize=1)
def get_language() ->Language:
    language = Language(lion_web_version=LionWebVersion.V2023_1, id=
        'library', name='library', key='library', version='1')
    Book = Concept(lion_web_version=LionWebVersion.V2023_1, id=
        'library-Book', name='Book', key='library-Book')
    language.add_element(Book)
    Library = Concept(lion_web_version=LionWebVersion.V2023_1, id=
        'library-Library', name='Library', key='library-Library')
    language.add_element(Library)
    Writer = Concept(lion_web_version=LionWebVersion.V2023_1, id=
        'library-Writer', name='Writer', key='library-Writer')
    language.add_element(Writer)
    GuideBookWriter = Concept(lion_web_version=LionWebVersion.V2023_1, id=
        'library-GuideBookWriter', name='GuideBookWriter', key=
        'library-GuideBookWriter')
    language.add_element(GuideBookWriter)
    SpecialistBookWriter = Concept(lion_web_version=LionWebVersion.V2023_1,
        id='library-SpecialistBookWriter', name='SpecialistBookWriter', key
        ='library-SpecialistBookWriter')
    language.add_element(SpecialistBookWriter)
    return language


def get_book() ->Concept:
    return get_language().get_concept_by_name('Book')


def get_library() ->Concept:
    return get_language().get_concept_by_name('Library')


def get_writer() ->Concept:
    return get_language().get_concept_by_name('Writer')


def get_guidebookwriter() ->Concept:
    return get_language().get_concept_by_name('GuideBookWriter')


def get_specialistbookwriter() ->Concept:
    return get_language().get_concept_by_name('SpecialistBookWriter')
