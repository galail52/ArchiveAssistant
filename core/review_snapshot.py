from copy import deepcopy
from dataclasses import dataclass

from core.review_state import ReviewState


@dataclass(slots=True)
class ReviewSnapshot:
    file_path: str
    state: ReviewState

    @classmethod
    def capture(cls, file_path, state):
        return cls(
            str(file_path),
            deepcopy(state),
        )