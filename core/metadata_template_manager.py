from dataclasses import dataclass

from core.metadata_state import MetadataState


DEFAULT_TEMPLATE_CATEGORY = "general"


@dataclass
class MetadataTemplate:
    id: int
    name: str
    category: str
    metadata: MetadataState


class MetadataTemplateManager:
    def __init__(self, database, category=DEFAULT_TEMPLATE_CATEGORY):
        self.database = database
        self.category = category

    def templates(self):
        return self.database.list_metadata_templates(self.category)

    def save_template(self, name: str, metadata: MetadataState):
        return self.database.save_metadata_template(
            name.strip(),
            self.category,
            metadata,
        )

    def rename_template(self, template_id: int, name: str):
        return self.database.rename_metadata_template(
            template_id,
            name.strip(),
        )

    def delete_template(self, template_id: int):
        return self.database.delete_metadata_template(template_id)

    def template(self, template_id: int):
        return self.database.get_metadata_template(template_id)
