from dataclasses import dataclass
from typing import Optional

from lionweb.model.node import ClassifierInstance
from lionweb.utils.issue_severity import IssueSeverity


@dataclass(frozen=False, eq=True, unsafe_hash=True)
class Issue:
    severity: IssueSeverity
    message: str
    subject: Optional[ClassifierInstance] = None

    def is_error(self) -> bool:
        return self.severity == IssueSeverity.ERROR
