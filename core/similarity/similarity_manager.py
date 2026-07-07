from collections import defaultdict

from core.similarity.fingerprint_engine import FingerprintEngine
from core.similarity.similarity_group import SimilarityGroup
from core.similarity.similarity_match import SimilarityMatch


class SimilarityManager:
    EXACT_THRESHOLD = 1.0
    SIMILAR_THRESHOLD = 0.92

    def __init__(self, fingerprint_engine=None):
        self.fingerprint_engine = fingerprint_engine or FingerprintEngine()
        self.fingerprints = {}
        self.matches = []
        self.groups = []
        self.skipped_images = []

    def scan(self, image_paths):
        self.clear_results()
        paths = [str(path) for path in image_paths]

        for image_path in paths:
            fingerprint = self.fingerprint_engine.fingerprint(image_path)

            if fingerprint is None:
                self.skipped_images.append(image_path)
                continue

            self.fingerprints[fingerprint.image_id] = fingerprint

        fingerprints = list(self.fingerprints.values())

        for index, source in enumerate(fingerprints):
            for target in fingerprints[index + 1:]:
                match = self.compare_fingerprints(source, target)

                if match is not None:
                    self.matches.append(match)

        self.groups = self.build_groups(self.matches)
        return self.groups

    def compare_fingerprints(self, source, target):
        score = self.fingerprint_engine.compare(source, target)

        if score >= self.EXACT_THRESHOLD:
            return SimilarityMatch(
                source_image_id=source.image_id,
                target_image_id=target.image_id,
                similarity_score=1.0,
                match_type="exact_duplicate",
                explanation="Fingerprints are identical.",
            )

        if score >= self.SIMILAR_THRESHOLD:
            return SimilarityMatch(
                source_image_id=source.image_id,
                target_image_id=target.image_id,
                similarity_score=round(score, 4),
                match_type="high_confidence_similar",
                explanation="Perceptual fingerprints are highly similar.",
            )

        return None

    def build_groups(self, matches):
        parent = {}

        def find(image_id):
            parent.setdefault(image_id, image_id)

            if parent[image_id] != image_id:
                parent[image_id] = find(parent[image_id])

            return parent[image_id]

        def union(source, target):
            source_root = find(source)
            target_root = find(target)

            if source_root != target_root:
                parent[target_root] = source_root

        for match in matches:
            union(match.source_image_id, match.target_image_id)

        grouped_ids = defaultdict(list)

        for image_id in parent:
            grouped_ids[find(image_id)].append(image_id)

        groups = []

        for index, image_ids in enumerate(grouped_ids.values(), start=1):
            image_set = set(image_ids)
            group_matches = tuple(
                match
                for match in matches
                if (
                    match.source_image_id in image_set
                    and match.target_image_id in image_set
                )
            )
            groups.append(
                SimilarityGroup(
                    group_id=f"similarity-{index}",
                    image_ids=tuple(sorted(image_ids)),
                    matches=group_matches,
                )
            )

        return groups

    def matches_for_image(self, image_id):
        image_id = str(image_id)

        return [
            match
            for match in self.matches
            if (
                match.source_image_id == image_id
                or match.target_image_id == image_id
            )
        ]

    def candidate_groups(self):
        return list(self.groups)

    def clear_results(self):
        self.fingerprints = {}
        self.matches = []
        self.groups = []
        self.skipped_images = []
