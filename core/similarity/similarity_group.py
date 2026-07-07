from dataclasses import dataclass

from core.similarity.similarity_match import SimilarityMatch


@dataclass(frozen=True)
class SimilarityGroup:
    group_id: str
    image_ids: tuple[str, ...]
    matches: tuple[SimilarityMatch, ...]
