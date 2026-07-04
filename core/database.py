import sqlite3
from pathlib import Path

from core.review_state import ReviewState


class ArchiveDatabase:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row

        self.create_tables()
        self.migrate_tables()

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
                delete_flag INTEGER NOT NULL DEFAULT 0,

                notes TEXT DEFAULT '',
                people TEXT DEFAULT '',
                location TEXT DEFAULT '',
                date_taken TEXT DEFAULT '',

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

        if "reviewed" not in columns:
            self.connection.execute(
                """
                ALTER TABLE photos
                ADD COLUMN reviewed INTEGER NOT NULL DEFAULT 0
                """
            )

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
                delete_flag = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE file_path = ?
            """,
            (
                state.rotation,
                int(state.has_back),
                int(state.favorite),
                int(state.needs_restore),
                int(state.delete),
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

    def get_stats(self, project_path: Path):
        row = self.connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(reviewed) AS reviewed,
                SUM(has_back) AS backs,
                SUM(favorite) AS favorites,
                SUM(needs_restore) AS restore,
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
            "deletes": row["deletes"] or 0,
        }