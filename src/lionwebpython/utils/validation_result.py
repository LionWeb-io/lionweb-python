from typing import Set

from lionwebpython.model.node import Node
from lionwebpython.utils.issue import Issue
from lionwebpython.utils.issue_severity import IssueSeverity


class ValidationResult:
    def __init__(self):
        self.issues: Set[Issue] = set()

    def get_issues(self) -> Set[Issue]:
        return self.issues

    def is_successful(self) -> bool:
        return all(issue.get_severity() != IssueSeverity.ERROR for issue in self.issues)

    def add_error(self, message: str, subject: Node) -> "ValidationResult":
        self.issues.add(Issue(IssueSeverity.ERROR, message, subject))
        return self

    def check_for_error(
        self, check: bool, message: str, subject: Node
    ) -> "ValidationResult":
        if check:
            self.issues.add(Issue(IssueSeverity.ERROR, message, subject))
        return self

    def __str__(self):
        return f"ValidationResult({', '.join(str(issue) for issue in self.issues)})"
