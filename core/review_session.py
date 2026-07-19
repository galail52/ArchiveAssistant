from pathlib import Path

from core.ai import AIManager, ArchiveAdvisoryClient, OCRCleanupReview
from core.database import ArchiveDatabase
from core.export import ExportFormat
from core.export import ExportJob
from core.export import ExportManager
from core.health import HealthManager
from core.image_manager import ImageManager
from core.metadata import parse_people
from core.metadata_patch import MetadataPatch
from core.metadata_state import RECENT_METADATA_FIELDS
from core.metadata_state import MetadataState
from core.metadata_template_manager import MetadataTemplateManager
from core.navigator import Navigator
from core.ocr import OCRManager
from core.relationships import RelationshipManager
from core.relationships import RelationshipType
from core.review_snapshot import ReviewSnapshot
from core.review_state import ReviewState
from core.search import SmartFilterManager
from core.similarity import SimilarityManager
from core.view_state import ViewState


class ReviewSession:
    def __init__(self):
        self.images = ImageManager()
        self.navigator = Navigator(self.images)
        self.review_state = ReviewState()
        self.view_state = ViewState()
        self.metadata_state = MetadataState()
        self.metadata_clipboard = None
        self.metadata_patch_clipboard = None
        self.last_snapshot = None
        self.previous_jump_index = None
        self._stats_cache = None

        self.database = ArchiveDatabase(
            Path("data") / "archive.db"
        )
        self.template_manager = MetadataTemplateManager(self.database)
        self.export_manager = ExportManager()
        self.health_manager = HealthManager(self.database)
        self.smart_filter_manager = SmartFilterManager(self.database)
        self.ocr_manager = OCRManager()
        self.relationship_manager = RelationshipManager(self.database)
        self.similarity_manager = SimilarityManager()
        self.ai_manager = AIManager()
        self.archive_advisory = ArchiveAdvisoryClient(self.ai_manager)

    def close(self):
        database = getattr(self, "database", None)

        if database is not None:
            database.close()

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    @property
    def state(self):
        return self.review_state

    @property
    def metadata(self):
        return self.metadata_state

    def open_project(self, folder: str | Path):
        self.images.open_project(folder)
        self.view_state.reset()
        self.metadata_state.reset()
        self.last_snapshot = None
        self.previous_jump_index = None
        self._stats_cache = None

        for file_path in self.images.files:
            self.database.ensure_photo(
                self.images.project_path,
                file_path,
            )

        last_viewed = self.database.get_last_viewed_path(
            self.images.project_path
        )

        if last_viewed in self.images.files:
            self.images.index = self.images.files.index(last_viewed)

        self.load_current_state()

    def check_project_health(self):
        if self.images.project_path is None:
            return None

        return self.database.check_project_health(
            self.images.project_path,
            self.images.files,
        )

    def load_current_state(self):
        current = self.current_file

        if current is None:
            self.review_state.reset()
            self.view_state.reset()
            self.metadata_state.reset()
            self.last_snapshot = None
            return

        self.review_state = self.database.load_state(current)
        self.metadata_state = self.database.load_metadata(current)
        self.view_state.set_rotation(self.review_state.rotation)
        self.database.mark_last_viewed(current)

    def take_snapshot(self):
        current = self.current_file

        if current is None:
            return

        self.last_snapshot = ReviewSnapshot.capture(
            current,
            self.review_state,
        )

    def can_undo(self):
        return (
            self.last_snapshot is not None
            and self.current_file is not None
            and str(self.current_file) == self.last_snapshot.file_path
        )

    def undo_last_review_change(self):
        if not self.can_undo():
            return False

        self.review_state = self.last_snapshot.state
        self.view_state.set_rotation(self.review_state.rotation)
        self.last_snapshot = None
        self.save_current_state()
        return True

    def save_current_state(self):
        current = self.current_file

        if current is None:
            return

        self.database.save_state(current, self.review_state)
        self.database.mark_last_viewed(current)
        self._stats_cache = None

    def save_current_metadata(self):
        current = self.current_file

        if current is None:
            return

        self.database.save_metadata(current, self.metadata_state)

    def update_metadata(
        self,
        people: str,
        event: str,
        location: str,
        date_taken: str,
        keywords: str,
        notes: str,
        note_by: str,
        confidence: int,
    ):
        self.metadata_state = MetadataState(
            people=people,
            event=event,
            location=location,
            date_taken=date_taken,
            keywords=keywords,
            notes=notes,
            note_by=note_by,
            confidence=confidence,
        )
        self.save_current_metadata()

    def can_copy_metadata_from_previous(self):
        return self.image_count > 0 and self.images.index > 0

    def copy_metadata_from_previous(self):
        if not self.can_copy_metadata_from_previous():
            return False

        previous_file = self.images.files[self.images.index - 1]
        self.metadata_state = self.database.load_metadata(previous_file)
        self.save_current_metadata()
        return True

    def can_copy_metadata(self):
        return self.current_file is not None

    def copy_metadata(self):
        if not self.can_copy_metadata():
            return False

        self.metadata_clipboard = self.metadata_state.copy()
        return True

    def can_paste_metadata(self):
        return (
            self.current_file is not None
            and self.metadata_clipboard is not None
        )

    def paste_metadata(self):
        if not self.can_paste_metadata():
            return False

        self.metadata_state = self.metadata_clipboard.copy()
        self.save_current_metadata()
        return True

    def copy_selected_metadata(self, fields):
        if not self.can_copy_metadata():
            return False

        patch = MetadataPatch.from_metadata(self.metadata_state, fields)

        if not patch.fields:
            return False

        self.metadata_patch_clipboard = patch
        return True

    def can_paste_selected_metadata(self):
        return (
            self.current_file is not None
            and self.metadata_patch_clipboard is not None
            and bool(self.metadata_patch_clipboard.fields)
        )

    def paste_selected_metadata(self, fields=None):
        if not self.can_paste_selected_metadata():
            return False

        patch = self.metadata_patch_clipboard

        if fields is not None:
            selected_values = {
                field: patch.values[field]
                for field in fields
                if field in patch.values
            }
            patch = MetadataPatch(selected_values)

        if not patch.fields:
            return False

        self.metadata_state = patch.apply_to(self.metadata_state)
        self.save_current_metadata()
        return True

    def recent_metadata_values(self):
        if self.images.project_path is None:
            return {field: [] for field in RECENT_METADATA_FIELDS}

        values = {
            field: self.database.recent_metadata_values(
                self.images.project_path,
                field,
            )
            for field in RECENT_METADATA_FIELDS
        }

        people = []
        seen = set()

        for value in values["people"]:
            for person in parse_people(value):
                key = person.lower()

                if key not in seen:
                    seen.add(key)
                    people.append(person)

        values["people"] = people[:20]
        return values

    def metadata_templates(self):
        return self.template_manager.templates()

    def save_current_metadata_template(self, name: str):
        if self.current_file is None:
            return None

        return self.template_manager.save_template(name, self.metadata_state)

    def apply_metadata_template(self, template_id: int):
        if self.current_file is None:
            return False

        template = self.template_manager.template(template_id)

        if template is None:
            return False

        self.metadata_state = template.metadata.copy()
        self.save_current_metadata()
        return True

    def rename_metadata_template(self, template_id: int, name: str):
        return self.template_manager.rename_template(template_id, name)

    def delete_metadata_template(self, template_id: int):
        return self.template_manager.delete_template(template_id)

    def export_records(self):
        if self.images.project_path is None:
            return []

        return self.database.export_records(self.images.project_path)

    def export_metadata(
        self,
        export_format: ExportFormat,
        output_path: Path,
        dry_run=True,
    ):
        if self.images.project_path is None:
            return None

        job = ExportJob(
            format=export_format,
            project_path=self.images.project_path,
            output_path=output_path,
            dry_run=dry_run,
        )

        return self.export_manager.export(job, self.export_records())

    def export_preview(self):
        if self.images.project_path is None:
            return None

        return self.export_metadata(
            ExportFormat.JSON,
            self.images.project_path / "archiveassistant_export_preview.json",
            dry_run=True,
        )

    def build_health_report(self):
        if self.images.project_path is None:
            return None

        return self.health_manager.build_report(self.images.project_path)

    def list_smart_filters(self):
        return self.smart_filter_manager.list_filters()

    def smart_filter_matches(self, filter_id):
        if self.images.project_path is None:
            return []

        return self.smart_filter_manager.matching_records(
            self.images.project_path,
            filter_id,
        )

    def apply_smart_filter(self, filter_id):
        matches = self.smart_filter_matches(filter_id)

        if not matches:
            return []

        first_match = matches[0]

        if first_match.file_path in self.images.files:
            self.jump_to(self.images.files.index(first_match.file_path))

        return matches

    def build_ocr_queue(self):
        return self.ocr_manager.queue

    def ocr_status(self):
        return self.ocr_manager.status_counts()

    def queue_current_for_ocr(self, source_type="unknown", replace_existing=False):
        if self.current_file is None:
            return None

        return self.ocr_manager.queue_image(
            self.current_file,
            source_type,
            replace_existing=replace_existing,
        )

    def queue_missing_ocr(self, source_type="unknown"):
        if self.images.project_path is None:
            return []

        return self.ocr_manager.queue_missing(
            self.export_records(),
            source_type,
        )

    def run_current_ocr(self, source_type="unknown"):
        job = self.queue_current_for_ocr(
            source_type,
            replace_existing=True,
        )

        if job is None:
            return None

        return self.ocr_manager.execute_job(job)

    def run_ocr_queue(self):
        return self.ocr_manager.run_queue()

    def latest_ocr_result(self):
        return self.ocr_manager.latest_result()

    def scan_image_similarity(self):
        if self.images.project_path is None:
            return []

        return self.similarity_manager.scan(self.images.files)

    def similarity_groups(self):
        return self.similarity_manager.candidate_groups()

    def similarity_matches_for_image(self, image_id=None):
        if image_id is None:
            image_id = self.current_file

        if image_id is None:
            return []

        return self.similarity_manager.matches_for_image(image_id)

    def clear_similarity_results(self):
        self.similarity_manager.clear_results()

    def ai_status(self):
        return self.ai_manager.status()

    def test_ai_connection(self):
        return self.ai_manager.test_connection()

    def list_ai_models(self):
        return self.ai_manager.list_models()

    def send_ai_test_prompt(self):
        return self.ai_manager.send_test_prompt()

    def clean_latest_ocr_with_ai(self):
        ocr_result = self.latest_ocr_result()
        if ocr_result is None or not ocr_result.raw_text.strip():
            return None, "Run OCR on the current image before requesting cleanup."

        suggestion = self.archive_advisory.run(
            "ocr_cleanup",
            {"raw_ocr_text": ocr_result.raw_text},
        )
        if not suggestion.success:
            error = suggestion.error or {}
            return None, error.get("message") or "AI OCR cleanup failed."

        try:
            review = OCRCleanupReview.from_result(
                suggestion.result,
                fallback_original=ocr_result.raw_text,
            )
        except ValueError as error:
            return None, str(error)

        return review, ""

    def add_ocr_text_to_metadata_notes(self, text):
        cleaned = str(text or "").strip()
        if not cleaned or self.current_file is None:
            return False

        existing = self.metadata_state.notes.strip()
        if cleaned == existing or cleaned in self._note_blocks(existing):
            return False

        notes = cleaned if not existing else f"{existing}\n\n{cleaned}"
        self.metadata_state = self.metadata_state.with_fields({"notes": notes})
        self.save_current_metadata()
        return True

    @staticmethod
    def _note_blocks(notes):
        return {
            block.strip()
            for block in str(notes or "").split("\n\n")
            if block.strip()
        }

    def run_current_ocr_with_ai_cleanup(self, source_type="unknown"):
        """Run OCR, then prepare a human-reviewed AI cleanup suggestion."""
        ocr_result = self.run_current_ocr(source_type)
        if ocr_result is None:
            return None, None, "No image selected for OCR."

        if not ocr_result.raw_text.strip():
            error = next(iter(ocr_result.errors), "")
            if not error:
                error = "OCR completed without extracted text."
            return ocr_result, None, error

        review, error = self.clean_latest_ocr_with_ai()
        return ocr_result, review, error

    def create_relationship(
        self,
        source_image_id,
        target_image_id,
        relationship_type=RelationshipType.FRONT_BACK,
        notes="",
    ):
        return self.relationship_manager.create_relationship(
            source_image_id,
            target_image_id,
            relationship_type,
            notes,
        )

    def create_current_relationship(
        self,
        target_image_id,
        relationship_type=RelationshipType.FRONT_BACK,
        notes="",
    ):
        if self.current_file is None:
            return None

        return self.create_relationship(
            self.current_file,
            target_image_id,
            relationship_type,
            notes,
        )

    def remove_relationship(self, relationship_id):
        return self.relationship_manager.remove_relationship(relationship_id)

    def related_images(self, image_id=None):
        if image_id is None:
            image_id = self.current_file

        if image_id is None:
            return []

        return self.relationship_manager.related_images(image_id)

    def relationships_for_image(self, image_id=None):
        if image_id is None:
            image_id = self.current_file

        if image_id is None:
            return []

        return self.relationship_manager.relationships_for_image(image_id)

    def has_relationship(self, image_id=None):
        if image_id is None:
            image_id = self.current_file

        if image_id is None:
            return False

        return self.relationship_manager.has_relationship(image_id)

    def relationship_records_for_current(self):
        return self.relationships_for_image()

    def jump_to_related_image(self, image_id):
        target = Path(image_id)

        if target not in self.images.files:
            return False

        return self.jump_to(self.images.files.index(target))

    def move(self, offset: int):
        return self.navigate(lambda: self.navigator.move(offset))

    def jump_by(self, offset: int):
        if self.image_count == 0:
            return False

        return self.jump_to(self.images.index + offset)

    def jump_to(self, index: int):
        if self.image_count == 0:
            return False

        target = max(0, min(index, self.image_count - 1))

        if target != self.images.index:
            self.previous_jump_index = self.images.index

        return self.navigate(lambda: self.navigator.jump_to(target))

    def can_return_to_previous_jump(self):
        return (
            self.image_count > 0
            and self.previous_jump_index is not None
            and 0 <= self.previous_jump_index < self.image_count
            and self.previous_jump_index != self.images.index
        )

    def return_to_previous_jump(self):
        if not self.can_return_to_previous_jump():
            return False

        target = self.previous_jump_index
        self.previous_jump_index = self.images.index
        return self.navigate(lambda: self.navigator.jump_to(target))

    def jump_to_first_unreviewed(self):
        for index, file_path in enumerate(self.images.files):
            if not self.database.is_reviewed(file_path):
                self.jump_to(index)
                return True

        return False

    def jump_to_next_research(self):
        return self.jump_to_next_matching(
            lambda _file_path, state: state.needs_research
        )

    def jump_to_next_unreviewed(self):
        return self.jump_to_next_matching(
            lambda file_path, _state: not self.database.is_reviewed(file_path)
        )

    def jump_to_next_favorite(self):
        return self.jump_to_next_matching(
            lambda _file_path, state: state.favorite
        )

    def jump_to_next_restore(self):
        return self.jump_to_next_matching(
            lambda _file_path, state: state.needs_restore
        )

    def jump_to_next_back(self):
        return self.jump_to_next_matching(
            lambda _file_path, state: state.has_back
        )

    def jump_to_next_delete(self):
        return self.jump_to_next_matching(
            lambda _file_path, state: state.delete
        )

    def jump_to_next_matching(self, predicate):
        if self.image_count == 0:
            return False

        start = self.images.index
        count = self.image_count

        for step in range(1, count + 1):
            index = (start + step) % count
            file_path = self.images.files[index]
            state = self.database.load_state(file_path)

            if predicate(file_path, state):
                self.jump_to(index)
                return True

        return False

    def first(self):
        return self.jump_to(0)

    def last(self):
        return self.jump_to(self.image_count - 1)

    def navigate(self, action):
        if self.image_count == 0:
            return False

        previous_file = self.current_file

        self.save_current_state()
        action()

        if self.current_file != previous_file:
            self.database.mark_reviewed(previous_file)
            self._stats_cache = None
            self.last_snapshot = None
            self.load_current_state()
            return True

        return False

    def next_image(self):
        return self.move(1)

    def previous_image(self):
        return self.move(-1)

    def set_zoom_fit(self):
        self.view_state.set_fit()

    def set_zoom_percent(self, percent: int):
        self.view_state.set_zoom_percent(percent)

    def zoom_in(self):
        self.view_state.zoom_in()

    def zoom_out(self):
        self.view_state.zoom_out()

    def pan_view(self, dx: int, dy: int):
        self.view_state.pan(dx, dy)

    def rotate_left(self):
        self.take_snapshot()
        self.review_state.rotate_left()
        self.view_state.set_rotation(self.review_state.rotation)
        self.save_current_state()

    def rotate_right(self):
        self.take_snapshot()
        self.review_state.rotate_right()
        self.view_state.set_rotation(self.review_state.rotation)
        self.save_current_state()

    def toggle_back(self):
        self.take_snapshot()
        self.review_state.toggle_back()
        self.save_current_state()

    def toggle_favorite(self):
        self.take_snapshot()
        self.review_state.toggle_favorite()
        self.save_current_state()

    def toggle_restore(self):
        self.take_snapshot()
        self.review_state.toggle_restore()
        self.save_current_state()

    def toggle_research(self):
        self.take_snapshot()
        self.review_state.toggle_research()
        self.save_current_state()

    def toggle_delete(self):
        self.take_snapshot()
        self.review_state.toggle_delete()
        self.save_current_state()

    def state_for_file(self, file_path: Path) -> ReviewState:
        if file_path == self.current_file:
            return self.review_state

        return self.database.load_state(file_path)

    @property
    def current_file(self):
        return self.images.current_file

    @property
    def progress(self):
        return self.images.progress

    @property
    def project_name(self):
        if self.images.project_path is None:
            return ""

        return self.images.project_path.name

    @property
    def image_count(self):
        return self.images.count

    @property
    def stats(self):
        if self.images.project_path is None:
            return {
                "total": 0,
                "reviewed": 0,
                "backs": 0,
                "favorites": 0,
                "restore": 0,
                "research": 0,
                "deletes": 0,
            }

        if self._stats_cache is None:
            self._stats_cache = self.database.get_stats(
                self.images.project_path
            )

        return self._stats_cache
