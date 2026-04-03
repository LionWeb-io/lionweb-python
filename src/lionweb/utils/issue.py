from dataclasses import dataclass

from lionweb.model.node import ClassifierInstance
from lionweb.utils.issue_severity import IssueSeverity


@dataclass(frozen=False, eq=True, unsafe_hash=True)
class Issue:
    severity: IssueSeverity
    message: str
    subject: ClassifierInstance | None = None

    def is_error(self) -> bool:
        return self.severity == IssueSeverity.ERROR
