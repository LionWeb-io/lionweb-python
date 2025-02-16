from lionwebpython.language.concept import Concept
from lionwebpython.language.containment import Containment
from lionwebpython.language.language import Language
from lionwebpython.language.reference import Reference


class RefsLanguage(Language):
    INSTANCE = None
    CONTAINER_NODE = None
    REF_NODE = None

    def __init__(self):
        super().__init__()
        self.id = "Refs"
        self.key = "Refs"
        self.name = "Refs"
        self.version = "1"

        # We do not pass INSTANCE as it is still None at this point
        RefsLanguage.CONTAINER_NODE = Concept(name="Container", id="RefsMM_Container")
        RefsLanguage.CONTAINER_NODE.key = "RefsMM_Container"
        RefsLanguage.REF_NODE = Concept(name="Ref", id="RefsMM_Ref")
        RefsLanguage.REF_NODE.key = "RefsMM_Ref"

        self.add_element(RefsLanguage.CONTAINER_NODE)
        self.add_element(RefsLanguage.REF_NODE)

        RefsLanguage.CONTAINER_NODE.add_feature(
            Containment.create_optional("contained", RefsLanguage.CONTAINER_NODE)
            .set_id("RefsMM_Container_contained")
            .set_key("RefsMM_Container_contained")
        )

        RefsLanguage.REF_NODE.add_feature(
            Reference.create_optional("referred", RefsLanguage.REF_NODE)
            .set_id("RefsMM_Ref_referred")
            .set_key("RefsMM_Ref_referred")
        )


# Initialize the singleton instance
RefsLanguage.INSTANCE = RefsLanguage()
