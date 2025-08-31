from lionweb import LionWebVersion
from lionweb.language import Language
from lionweb.self.lioncore import LionCore
from lionweb.utils.model_comparator import ComparisonResult, ModelComparator


def compare_languages(language_a: Language, language_b: Language) -> ComparisonResult:
    comparator = ModelComparator(
        unordered_links=[
            LionCore.get_language(LionWebVersion.V2023_1).get_containment_by_name(
                "entities"
            ),
            LionCore.get_language(LionWebVersion.V2024_1).get_containment_by_name(
                "entities"
            ),
            LionCore.get_classifier(LionWebVersion.V2023_1).get_containment_by_name(
                "features"
            ),
            LionCore.get_classifier(LionWebVersion.V2024_1).get_containment_by_name(
                "features"
            ),
        ]
    )
    return comparator.compare(language_a, language_b)
