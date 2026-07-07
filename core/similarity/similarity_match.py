from dataclasses import dataclass


@dataclass(frozen=True)
class SimilarityMatch:
    source_image_id: str
    target_image_id: str
    similarity_score: float
    match_type: str
    explanation: str = ""
