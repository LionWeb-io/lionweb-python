from lionweb.language import (Annotation, Concept, Containment, Language,
                              Property)
from lionweb.language.lioncore_builtins import LionCoreBuiltins
from lionweb.model.impl.dynamic_annotation_instance import \
    DynamicAnnotationInstance


class MyAnnotation(DynamicAnnotationInstance):
    LANGUAGE = (
        Language()
        .set_id("myLanguageWithAnnotations-id")
        .set_key("myLanguageWithAnnotations-key")
        .set_name("LWA")
        .set_version("1")
    )

    ANNOTATION = Annotation(
        language=LANGUAGE,
        name="MyAnnotation",
        id="MyAnnotation-ID",
        key="ma",
    )

    VALUE = (
        Concept()
        .set_id("Value-id")
        .set_key("Value-key")
        .set_name("Value")
        .set_parent(LANGUAGE)
    )

    ANNOTATED = (
        Concept()
        .set_id("Annotated-id")
        .set_key("Annotated-key")
        .set_name("Annotated")
        .set_parent(LANGUAGE)
    )

    # Static initialization block equivalent in Python
    VALUE.add_feature(
        Property.create_required(name="amount", type=LionCoreBuiltins.get_integer())
        .set_key("my-amount")
        .set_id("my-amount")
    )

    ANNOTATION.annotates = ANNOTATED
    ANNOTATION.add_feature(
        Containment.create_multiple(name="values", type=VALUE)
        .set_key("my-values")
        .set_id("my-values")
    )

    LANGUAGE.add_element(ANNOTATION)
    LANGUAGE.add_element(VALUE)
    LANGUAGE.add_element(ANNOTATED)

    def __init__(self, id: str):
        super().__init__(id, MyAnnotation.ANNOTATION)
