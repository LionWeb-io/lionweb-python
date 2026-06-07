from lionweb.model import ClassifierInstance
from lionweb.utils.issue import Issue
from lionweb.utils.issue_severity import IssueSeverity


class ValidationResult:
    """Accumulates validation issues found while validating a model element."""

    def __init__(self) -> None:
        self.issues: set[Issue] = set()

    def get_issues(self) -> set[Issue]:
        """Return the set of issues collected so far."""
        return self.issues

    def is_successful(self) -> bool:
        """Return True if no error-level issues were recorded."""
        return not self.has_errors()

    def has_errors(self) -> bool:
        """Return True if at least one error-level issue was recorded."""
        return any(issue.is_error() for issue in self.issues)

    def add_error(self, message: str, subject: ClassifierInstance) -> "ValidationResult":
        """Record an error-level issue.

        Args:
            message: Description of the problem.
            subject: The classifier instance the issue refers to.

        Returns:
            ValidationResult: This instance, to allow chaining.
        """
        self.issues.add(Issue(IssueSeverity.ERROR, message, subject))
        return self

    def add_error_if(
        self, check: bool, message: str, subject: ClassifierInstance
    ) -> "ValidationResult":
        """Record an error-level issue only if `check` is True.

        Args:
            check: Condition that, when True, causes the issue to be recorded.
            message: Description of the problem.
            subject: The classifier instance the issue refers to.

        Returns:
            ValidationResult: This instance, to allow chaining.
        """
        if check:
            self.issues.add(Issue(IssueSeverity.ERROR, message, subject))
        return self

    def __str__(self) -> str:
        return f"ValidationResult({', '.join(str(issue) for issue in self.issues)})"

    def __bool__(self) -> bool:
        return not self.has_errors()
