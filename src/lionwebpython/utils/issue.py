from typing import Optional

from lionwebpython.model.node import Node
from lionwebpython.utils.issue_severity import IssueSeverity


class Issue:
    def __init__(
        self, severity: IssueSeverity, message: str, subject: Optional[Node] = None
    ):
        self.message = message
        self.severity = severity
        self.subject = subject

    def get_message(self) -> str:
        return self.message

    def get_severity(self) -> IssueSeverity:
        return self.severity

    def get_subject(self) -> Optional[Node]:
        return self.subject

    def __hash__(self):
        return hash((self.message, self.severity))

    def __eq__(self, other):
        if not isinstance(other, Issue):
            return False
        return (
            self.message == other.message
            and self.severity == other.severity
            and self.subject is other.subject
        )

    def __str__(self):
        return f"Issue(message='{self.message}', severity={self.severity}, subject={self.subject})"

    def __repr__(self):
        return f"Issue(message='{self.message}', severity={self.severity}, subject={self.subject})"

    def is_error(self) -> bool:
        return self.severity == IssueSeverity.ERROR
