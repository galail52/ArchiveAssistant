from pathlib import Path

from core.relationships.relationship import Relationship
from core.relationships.relationship_type import RelationshipType


class RelationshipManager:
    def __init__(self, database):
        self.database = database

    def create_relationship(
        self,
        source_image_id,
        target_image_id,
        relationship_type=RelationshipType.FRONT_BACK,
        notes="",
    ):
        source_image_id = self.normalize_image_id(source_image_id)
        target_image_id = self.normalize_image_id(target_image_id)

        if not source_image_id or not target_image_id:
            return None

        if source_image_id == target_image_id:
            return None

        relationship_type = self.normalize_type(relationship_type)

        existing = self.find_relationship(
            source_image_id,
            target_image_id,
            relationship_type,
        )

        if existing is not None:
            return existing

        return self.database.create_relationship(
            source_image_id,
            target_image_id,
            relationship_type,
            notes,
        )

    def remove_relationship(self, relationship_id):
        return self.database.remove_relationship(relationship_id)

    def relationships_for_image(self, image_id):
        return self.database.relationships_for_image(
            self.normalize_image_id(image_id)
        )

    def related_images(self, image_id):
        image_id = self.normalize_image_id(image_id)
        related = []

        for relationship in self.relationships_for_image(image_id):
            if relationship.source_image_id == image_id:
                related.append(relationship.target_image_id)
            else:
                related.append(relationship.source_image_id)

        return related

    def has_relationship(
        self,
        source_image_id,
        target_image_id=None,
        relationship_type=None,
    ):
        if target_image_id is None:
            return bool(self.relationships_for_image(source_image_id))

        return self.find_relationship(
            source_image_id,
            target_image_id,
            relationship_type,
        ) is not None

    def find_relationship(
        self,
        source_image_id,
        target_image_id,
        relationship_type=None,
    ):
        source_image_id = self.normalize_image_id(source_image_id)
        target_image_id = self.normalize_image_id(target_image_id)

        if relationship_type is not None:
            relationship_type = self.normalize_type(relationship_type)

        for relationship in self.relationships_for_image(source_image_id):
            same_pair = {
                relationship.source_image_id,
                relationship.target_image_id,
            } == {source_image_id, target_image_id}

            if not same_pair:
                continue

            if (
                relationship_type is None
                or relationship.relationship_type == relationship_type
            ):
                return relationship

        return None

    def validate_relationship(self, relationship: Relationship):
        if relationship.source_image_id == relationship.target_image_id:
            return False

        if not relationship.source_image_id or not relationship.target_image_id:
            return False

        return True

    def normalize_image_id(self, image_id):
        if image_id is None:
            return ""

        return str(Path(image_id))

    def normalize_type(self, relationship_type):
        if isinstance(relationship_type, RelationshipType):
            return relationship_type

        return RelationshipType(str(relationship_type))
