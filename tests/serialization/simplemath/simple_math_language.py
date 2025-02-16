from lionwebpython.language.concept import Concept
from lionwebpython.language.containment import Containment
from lionwebpython.language.language import Language
from lionwebpython.language.lioncore_builtins import LionCoreBuiltins
from lionwebpython.language.property import Property


class SimpleMathLanguage(Language):
    INSTANCE = None
    INT_LITERAL = None
    SUM = None

    def __init__(self):
        super().__init__()
        self.set_id("SimpleMath")
        self.set_key("SimpleMath")
        self.set_name("SimpleMath")
        self.set_version("1")

        # Initialize concepts
        self.__class__.INT_LITERAL = Concept(
            name="IntLiteral", id="SimpleMath_IntLiteral"
        )
        self.__class__.INT_LITERAL.set_key("SimpleMath_IntLiteral")
        self.__class__.SUM = Concept(name="Sum", id="SimpleMath_Sum")
        self.__class__.SUM.set_key("SimpleMath_Sum")

        self.add_element(self.__class__.INT_LITERAL)
        self.add_element(self.__class__.SUM)

        # Add features to SUM
        self.__class__.SUM.add_feature(
            Containment.create_required("left", self.__class__.INT_LITERAL)
            .set_id("SimpleMath_Sum_left")
            .set_key("SimpleMath_Sum_left")
        )
        self.__class__.SUM.add_feature(
            Containment.create_required("right", self.__class__.INT_LITERAL)
            .set_id("SimpleMath_Sum_right")
            .set_key("SimpleMath_Sum_right")
        )

        # Add property to INT_LITERAL
        self.__class__.INT_LITERAL.add_feature(
            Property.create_required(name="value", type=LionCoreBuiltins.get_integer())
            .set_id("SimpleMath_IntLiteral_value")
            .set_key("SimpleMath_IntLiteral_value")
        )


SimpleMathLanguage.INSTANCE = SimpleMathLanguage()
