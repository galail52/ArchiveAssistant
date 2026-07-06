import shutil
import sqlite3
from pathlib import Path

from core.metadata_state import MetadataState
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