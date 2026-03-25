import os
import sqlite3
import numpy as np
import io
from datetime import datetime


class GlacierChangeEvent:
    def __init__(self, component, field, change, start_time, end_time):
        self.component = component
        self.field = field
        self.change = change
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return f"GlacierChangeEvent(component={self.component!r}, " f"field={self.field!r}, start_time={self.start_time!r}, " f"end_time={self.end_time!r})"


class GlacierHistory:
    def __init__(self, db_path="glacier_history.db"):
        # Delete the file if it exists
        if os.path.exists(db_path):
            os.remove(db_path)

        self.conn = sqlite3.connect(":memory:")
        self._init_db()
        self.event_list = []

    # ----------------------------
    # DB setup
    # ----------------------------
    def _init_db(self):
        cursor = self.conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS glacier_change_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component TEXT,
                field TEXT,
                change BLOB,
                start_time REAL,
                end_time REAL
            )
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_time
            ON glacier_change_events(start_time, end_time)
        """
        )

        self.conn.commit()

    # ----------------------------
    # Array <-> BLOB helpers
    # ----------------------------
    @staticmethod
    def _array_to_blob(arr: np.ndarray) -> bytes:
        buffer = io.BytesIO()
        np.save(buffer, arr)
        return buffer.getvalue()

    # ----------------------------
    # Insert
    # ----------------------------
    def add_event(self, event: GlacierChangeEvent):
        cursor = self.conn.cursor()

        blob = self._array_to_blob(event.change)

        cursor.execute(
            """
            INSERT INTO glacier_change_events
            (component, field, change, start_time, end_time)
            VALUES (?, ?, ?, ?, ?)
        """,
            (event.component.__class__.__name__, event.field, blob, event.start_time, event.end_time),
        )

        self.conn.commit()

    def add_event_to_list(self, event: GlacierChangeEvent):
        self.event_list.append(event)

    def bulk_add_event_list(self):
        cursor = self.conn.cursor()

        data = [
            (
                e.component.__class__.__name__,
                e.field,
                GlacierHistory._array_to_blob(e.change),
                e.start_time,
                e.end_time,
            )
            for e in self.event_list
        ]

        cursor.executemany(
            """
            INSERT INTO glacier_change_events
            (component, field, change, start_time, end_time)
            VALUES (?, ?, ?, ?, ?)
            """,
            data,
        )

        self.conn.commit()

    # ----------------------------
    # Close connection
    # ----------------------------
    def close(self):
        self.conn.close()
