import shutil
import sqlite3
from pathlib import Path

from core.export.models import ExportRecord
from core.metadata_state import RECENT_METADATA_FIELDS
from core.metadata_state import MetadataState
from core.metadata_template_manager import MetadataTemplate
from core.relationships import Relationship
from core.relationships import RelationshipType
from core.review_state import ReviewState


class ArchiveDatabase:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.backup_database()

        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row

        self.create_tables()
        self.migrate_tables()

    def backup_database(self):
        if not self.db_path.exists():
            return

        backup1 = self.db_path.with_suffix(
            self.db_path.suffix + ".backup1"
        )
        backup2 = self.db_path.with_suffix(
            self.db_path.suffix + ".backup2"
        )

        if backup2.exists():
            backup2.unlink()

        if backup1.exists():
            backup1.rename(backup2)

        shutil.copy2(self.db_path, backup1)

        if backup1.stat().st_size != self.db_path.stat().st_size:
            raise RuntimeError(
                "Database backup failed size verification."
            )

    def create_tables(self):
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_path TEXT NOT NULL,
                file_path TEXT NOT NULL UNIQUE,
                filename TEXT NOT NULL,

                rotation INTEGER NOT NULL DEFAULT 0,
                has_back INTEGER NOT NULL DEFAULT 0,
                favorite INTEGER NOT NULL DEFAULT 0,
                needs_restore INTEGER NOT NULL DEFAULT 0,
                needs_research INTEGER NOT NULL DEFAULT 0,
                delete_flag INTEGER NOT NULL DEFAULT 0,

                people TEXT DEFAULT '',
                event TEXT DEFAULT '',
                location TEXT DEFAULT '',
                date_taken TEXT DEFAULT '',
                keywords TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                note_by TEXT DEFAULT '',
                confidence INTEGER NOT NULL DEFAULT 0,

                reviewed INTEGER NOT NULL DEFAULT 0,
                last_viewed INTEGER NOT NULL DEFAULT 0,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self.connection.commit()

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'general',

                people TEXT DEFAULT '',
                event TEXT DEFAULT '',
                location TEXT DEFAULT '',
                date_taken TEXT DEFAULT '',
                keywords TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                note_by TEXT DEFAULT '',
                confidence INTEGER NOT NULL DEFAULT 0,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(name, category)
            )
            """
        )

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata_recent_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_path TEXT NOT NULL,
                field_name TEXT NOT NULL,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_image_id TEXT NOT NULL,
                target_image_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(
                    source_image_id,
                    target_image_id,
                    relationship_type
                )
            )
            """
        )

        self.connection.commit()

    def migrate_tables(self):
        columns = {
            row["name"]
            for row in self.connection.execute(
                "PRAGMA table_info(photos)"
            ).fetchall()
        }

        migrations = {
            "reviewed": """
                ALTER TABLE photos
                ADD COLUMN reviewed INTEGER NOT NULL DEFAULT 0
            """,
            "needs_research": """
                ALTER TABLE photos
                ADD COLUMN needs_research INTEGER NOT NULL DEFAULT 0
            """,
            "people": """
                ALTER TABLE photos
                ADD COLUMN people TEXT DEFAULT ''
            """,
            "event": """
                ALTER TABLE photos
                ADD COLUMN event TEXT DEFAULT ''
            """,
            "location": """
                ALTER TABLE photos
                ADD COLUMN location TEXT DEFAULT ''
            """,
            "date_taken": """
                ALTER TABLE photos
                ADD COLUMN date_taken TEXT DEFAULT ''
            """,
            "keywords": """
                ALTER TABLE photos
                ADD COLUMN keywords TEXT DEFAULT ''
            """,
            "notes": """
                ALTER TABLE photos
                ADD COLUMN notes TEXT DEFAULT ''
            """,
            "note_by": """
                ALTER TABLE photos
                ADD COLUMN note_by TEXT DEFAULT ''
            """,
            "confidence": """
                ALTER TABLE photos
                ADD COLUMN confidence INTEGER NOT NULL DEFAULT 0
            """,
        }

        for column, sql in migrations.items():
            if column not in columns:
                self.connection.execute(sql)

        self.connection.commit()

    def ensure_photo(self, project_path: Path, file_path: Path):
        self.connection.execute(
            """
            INSERT OR IGNORE INTO photos (
                project_path,
                file_path,
                filename
            )
            VALUES (?, ?, ?)
            """,
            (
                str(project_path),
                str(file_path),
                file_path.name,
            ),
        )

        self.connection.commit()

    def load_state(self, file_path: Path) -> ReviewState:
        row = self.connection.execute(
            """
            SELECT
                rotation,
                has_back,
                favorite,
                needs_restore,
                needs_research,
                delete_flag
            FROM photos
            WHERE file_path = ?
            """,
            (str(file_path),),
        ).fetchone()

        if row is None:
            return ReviewState()

        return ReviewState(
            rotation=row["rotation"],
            has_back=bool(row["has_back"]),
            favorite=bool(row["favorite"]),
            needs_restore=bool(row["needs_restore"]),
            needs_research=bool(row["needs_research"]),
            delete=bool(row["delete_flag"]),
        )

    def save_state(self, file_path: Path, state: ReviewState):
        self.connection.execute(
            """
            UPDATE photos
            SET
                rotation = ?,
                has_back = ?,
                favorite = ?,
                needs_restore = ?,
                needs_research = ?,
                delete_flag = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE file_path = ?
            """,
            (
                state.rotation,
                int(state.has_back),
                int(state.favorite),
                int(state.needs_restore),
                int(state.needs_research),
                int(state.delete),
                str(file_path),
            ),
        )

        self.connection.commit()

    def load_metadata(self, file_path: Path) -> MetadataState:
        row = self.connection.execute(
            """
            SELECT
                people,
                event,
                location,
                date_taken,
                keywords,
                notes,
                note_by,
                confidence
            FROM photos
            WHERE file_path = ?
            """,
            (str(file_path),),
        ).fetchone()

        if row is None:
            return MetadataState()

        return MetadataState(
            people=row["people"] or "",
            event=row["event"] or "",
            location=row["location"] or "",
            date_taken=row["date_taken"] or "",
            keywords=row["keywords"] or "",
            notes=row["notes"] or "",
            note_by=row["note_by"] or "",
            confidence=row["confidence"] or 0,
        )

    def save_metadata(self, file_path: Path, metadata: MetadataState):
        self.connection.execute(
            """
            UPDATE photos
            SET
                people = ?,
                event = ?,
                location = ?,
                date_taken = ?,
                keywords = ?,
                notes = ?,
                note_by = ?,
                confidence = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE file_path = ?
            """,
            (
                metadata.people,
                metadata.event,
                metadata.location,
                metadata.date_taken,
                metadata.keywords,
                metadata.notes,
                metadata.note_by,
                metadata.confidence,
                str(file_path),
            ),
        )

        self.connection.commit()
        self.remember_recent_metadata_values(file_path, metadata)

    def mark_reviewed(self, file_path: Path):
        self.connection.execute(
            """
            UPDATE photos
            SET reviewed = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE file_path = ?
            """,
            (str(file_path),),
        )

        self.connection.commit()

    def is_reviewed(self, file_path: Path):
        row = self.connection.execute(
            """
            SELECT reviewed
            FROM photos
            WHERE file_path = ?
            """,
            (str(file_path),),
        ).fetchone()

        if row is None:
            return False

        return bool(row["reviewed"])

    def mark_last_viewed(self, file_path: Path):
        self.connection.execute(
            """
            UPDATE photos
            SET last_viewed = 0
            """
        )

        self.connection.execute(
            """
            UPDATE photos
            SET last_viewed = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE file_path = ?
            """,
            (str(file_path),),
        )

        self.connection.commit()

    def get_last_viewed_path(self, project_path: Path) -> Path | None:
        row = self.connection.execute(
            """
            SELECT file_path
            FROM photos
            WHERE project_path = ?
              AND last_viewed = 1
            LIMIT 1
            """,
            (str(project_path),),
        ).fetchone()

        if row is None:
            return None

        return Path(row["file_path"])

    def get_project_files(self, project_path: Path):
        rows = self.connection.execute(
            """
            SELECT file_path
            FROM photos
            WHERE project_path = ?
            ORDER BY file_path
            """,
            (str(project_path),),
        ).fetchall()

        return [Path(row["file_path"]) for row in rows]

    def create_relationship(
        self,
        source_image_id: str,
        target_image_id: str,
        relationship_type: RelationshipType,
        notes="",
    ):
        cursor = self.connection.execute(
            """
            INSERT INTO relationships (
                source_image_id,
                target_image_id,
                relationship_type,
                notes
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                source_image_id,
                target_image_id,
                relationship_type.value,
                notes,
            ),
        )

        self.connection.commit()

        return self.get_relationship(cursor.lastrowid)

    def get_relationship(self, relationship_id: int):
        row = self.connection.execute(
            """
            SELECT *
            FROM relationships
            WHERE id = ?
            """,
            (relationship_id,),
        ).fetchone()

        if row is None:
            return None

        return self.relationship_from_row(row)

    def remove_relationship(self, relationship_id: int):
        cursor = self.connection.execute(
            """
            DELETE FROM relationships
            WHERE id = ?
            """,
            (relationship_id,),
        )

        self.connection.commit()
        return cursor.rowcount > 0

    def relationships_for_image(self, image_id: str):
        rows = self.connection.execute(
            """
            SELECT *
            FROM relationships
            WHERE source_image_id = ?
               OR target_image_id = ?
            ORDER BY created_at, id
            """,
            (image_id, image_id),
        ).fetchall()

        return [self.relationship_from_row(row) for row in rows]

    def all_relationships(self):
        rows = self.connection.execute(
            """
            SELECT *
            FROM relationships
            ORDER BY created_at, id
            """
        ).fetchall()

        return [self.relationship_from_row(row) for row in rows]

    def relationship_from_row(self, row):
        return Relationship(
            relationship_id=row["id"],
            source_image_id=row["source_image_id"],
            target_image_id=row["target_image_id"],
            relationship_type=RelationshipType(row["relationship_type"]),
            created_at=row["created_at"],
            notes=row["notes"] or "",
        )

    def export_records(self, project_path: Path):
        rows = self.connection.execute(
            """
            SELECT
                file_path,
                filename,
                rotation,
                has_back,
                favorite,
                needs_restore,
                needs_research,
                delete_flag,
                people,
                event,
                location,
                date_taken,
                keywords,
                notes,
                note_by,
                confidence,
                reviewed
            FROM photos
            WHERE project_path = ?
            ORDER BY file_path
            """,
            (str(project_path),),
        ).fetchall()

        return [
            ExportRecord(
                file_path=Path(row["file_path"]),
                filename=row["filename"],
                metadata=self.metadata_state_from_row(row),
                review_state=ReviewState(
                    rotation=row["rotation"],
                    has_back=bool(row["has_back"]),
                    favorite=bool(row["favorite"]),
                    needs_restore=bool(row["needs_restore"]),
                    needs_research=bool(row["needs_research"]),
                    delete=bool(row["delete_flag"]),
                ),
                reviewed=bool(row["reviewed"]),
            )
            for row in rows
        ]

    def project_path_for_file(self, file_path: Path):
        row = self.connection.execute(
            """
            SELECT project_path
            FROM photos
            WHERE file_path = ?
            """,
            (str(file_path),),
        ).fetchone()

        if row is None:
            return None

        return Path(row["project_path"])

    def remember_recent_metadata_values(self, file_path: Path, metadata: MetadataState):
        project_path = self.project_path_for_file(file_path)

        if project_path is None:
            return

        for field_name in RECENT_METADATA_FIELDS:
            value = " ".join(str(getattr(metadata, field_name, "") or "").split())

            if not value:
                continue

            self.connection.execute(
                """
                DELETE FROM metadata_recent_values
                WHERE project_path = ?
                  AND field_name = ?
                  AND lower(value) = lower(?)
                """,
                (str(project_path), field_name, value),
            )

            self.connection.execute(
                """
                INSERT INTO metadata_recent_values (
                    project_path,
                    field_name,
                    value
                )
                VALUES (?, ?, ?)
                """,
                (str(project_path), field_name, value),
            )

            rows = self.connection.execute(
                """
                SELECT id
                FROM metadata_recent_values
                WHERE project_path = ?
                  AND field_name = ?
                ORDER BY updated_at DESC, id DESC
                LIMIT -1 OFFSET 20
                """,
                (str(project_path), field_name),
            ).fetchall()

            for row in rows:
                self.connection.execute(
                    """
                    DELETE FROM metadata_recent_values
                    WHERE id = ?
                    """,
                    (row["id"],),
                )

        self.connection.commit()

    def recent_metadata_values(self, project_path: Path, field_name: str):
        if field_name not in RECENT_METADATA_FIELDS:
            return []

        rows = self.connection.execute(
            """
            SELECT value
            FROM metadata_recent_values
            WHERE project_path = ?
              AND field_name = ?
            ORDER BY updated_at DESC, id DESC
            LIMIT 20
            """,
            (str(project_path), field_name),
        ).fetchall()

        return [row["value"] for row in rows]

    def metadata_state_from_row(self, row):
        return MetadataState(
            people=row["people"] or "",
            event=row["event"] or "",
            location=row["location"] or "",
            date_taken=row["date_taken"] or "",
            keywords=row["keywords"] or "",
            notes=row["notes"] or "",
            note_by=row["note_by"] or "",
            confidence=row["confidence"] or 0,
        )

    def list_metadata_templates(self, category="general"):
        rows = self.connection.execute(
            """
            SELECT *
            FROM metadata_templates
            WHERE category = ?
            ORDER BY lower(name)
            """,
            (category,),
        ).fetchall()

        return [
            MetadataTemplate(
                id=row["id"],
                name=row["name"],
                category=row["category"],
                metadata=self.metadata_state_from_row(row),
            )
            for row in rows
        ]

    def get_metadata_template(self, template_id: int):
        row = self.connection.execute(
            """
            SELECT *
            FROM metadata_templates
            WHERE id = ?
            """,
            (template_id,),
        ).fetchone()

        if row is None:
            return None

        return MetadataTemplate(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            metadata=self.metadata_state_from_row(row),
        )

    def save_metadata_template(
        self,
        name: str,
        category: str,
        metadata: MetadataState,
    ):
        if not name:
            return None

        self.connection.execute(
            """
            INSERT INTO metadata_templates (
                name,
                category,
                people,
                event,
                location,
                date_taken,
                keywords,
                notes,
                note_by,
                confidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name, category) DO UPDATE SET
                people = excluded.people,
                event = excluded.event,
                location = excluded.location,
                date_taken = excluded.date_taken,
                keywords = excluded.keywords,
                notes = excluded.notes,
                note_by = excluded.note_by,
                confidence = excluded.confidence,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                name,
                category,
                metadata.people,
                metadata.event,
                metadata.location,
                metadata.date_taken,
                metadata.keywords,
                metadata.notes,
                metadata.note_by,
                metadata.confidence,
            ),
        )

        self.connection.commit()

        row = self.connection.execute(
            """
            SELECT id
            FROM metadata_templates
            WHERE name = ?
              AND category = ?
            """,
            (name, category),
        ).fetchone()

        return row["id"] if row else None

    def rename_metadata_template(self, template_id: int, name: str):
        if not name:
            return False

        try:
            cursor = self.connection.execute(
                """
                UPDATE metadata_templates
                SET name = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (name, template_id),
            )
        except sqlite3.IntegrityError:
            return False

        self.connection.commit()
        return cursor.rowcount > 0

    def delete_metadata_template(self, template_id: int):
        cursor = self.connection.execute(
            """
            DELETE FROM metadata_templates
            WHERE id = ?
            """,
            (template_id,),
        )

        self.connection.commit()
        return cursor.rowcount > 0

    def check_project_health(
        self,
        project_path: Path,
        disk_files: list[Path],
    ):
        disk_set = {Path(file_path) for file_path in disk_files}
        db_set = set(self.get_project_files(project_path))

        missing_files = sorted(db_set - disk_set)
        new_files = sorted(disk_set - db_set)

        return {
            "disk_count": len(disk_set),
            "database_count": len(db_set),
            "missing_count": len(missing_files),
            "new_count": len(new_files),
            "missing_files": missing_files,
            "new_files": new_files,
            "healthy": (
                len(missing_files) == 0
                and len(new_files) == 0
            ),
        }

    def get_stats(self, project_path: Path):
        row = self.connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(reviewed) AS reviewed,
                SUM(has_back) AS backs,
                SUM(favorite) AS favorites,
                SUM(needs_restore) AS restore,
                SUM(needs_research) AS research,
                SUM(delete_flag) AS deletes
            FROM photos
            WHERE project_path = ?
            """,
            (str(project_path),),
        ).fetchone()

        return {
            "total": row["total"] or 0,
            "reviewed": row["reviewed"] or 0,
            "backs": row["backs"] or 0,
            "favorites": row["favorites"] or 0,
            "restore": row["restore"] or 0,
            "research": row["research"] or 0,
            "deletes": row["deletes"] or 0,
        }
