import os
import tempfile
import textwrap
import unittest
from typing import List

from lionweb.generation.language_generation import LanguageGenerator
from lionweb.language import LanguageFactory


class MockClick:

    messages: List[str] = []

    def echo(self, msg):
        self.messages.append(msg)


class LanguageGenerationTest(unittest.TestCase):

    def test_simple_generation(self):
        language_factory = LanguageFactory(name="MyLanguage")
        my_concept = language_factory.concept("MyConcept")
        language_factory.concept("MyOtherConcept").set_extends(my_concept)
        language = language_factory.build()

        mocked_click = MockClick()

        with tempfile.TemporaryDirectory() as outdir:
            LanguageGenerator().language_generation(mocked_click, language, outdir)
            rel_paths = [
                os.path.relpath(os.path.join(root, name), outdir)
                for root, dirs, files in os.walk(outdir)
                for name in dirs + files
            ]
            self.assertEqual(["language.py"], rel_paths)
            with open(os.path.join(outdir, "language.py"), encoding="utf-8") as f:
                content = f.read()
            expected = textwrap.dedent(
                """\
                from lionweb.language import Language, Concept, Containment, Enumeration, Interface, PrimitiveType, Property, Reference, LionCoreBuiltins
                from lionweb.lionweb_version import LionWebVersion
                from functools import lru_cache
                
                
                @lru_cache(maxsize=1)
                def get_language() ->Language:
                    language = Language(lion_web_version=LionWebVersion.V2024_1, id=
                        'MyLanguage', name='MyLanguage', key='MyLanguage', version='1')
                    my_concept = Concept(lion_web_version=LionWebVersion.V2024_1, id=
                        'MyLanguage_MyConcept', name='MyConcept', key='MyLanguage_MyConcept')
                    my_concept.abstract = False
                    my_concept.partition = False
                    language.add_element(my_concept)
                    my_other_concept = Concept(lion_web_version=LionWebVersion.V2024_1, id=
                        'MyLanguage_MyOtherConcept', name='MyOtherConcept', key=
                        'MyLanguage_MyOtherConcept')
                    my_other_concept.abstract = False
                    my_other_concept.partition = False
                    language.add_element(my_other_concept)
                    return language
                
                
                def get_my_concept() ->Concept:
                    return get_language().get_concept_by_name('MyConcept')
                
                
                def get_my_other_concept() ->Concept:
                    return get_language().get_concept_by_name('MyOtherConcept')
            """
            )
            self.assertEqual(expected, content)


if __name__ == "__main__":
    unittest.main()
