import os
import sqlite3
import numpy as np
import io

import pandas as pd
from core.components.model_component import ModelComponent


class GlacierChangeEvent:
    def __init__(self, component: ModelComponent, field: str, change: np.ndarray, start_time: pd.Timestamp, end_time: pd.Timestamp, subcomponent=""):
        self.component = component
        self.subcomponent = subcomponent
        self.field = field
        self.change = change
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return f"GlacierChangeEvent(component={self.component!r}, " f"field={self.field!r}, start_time={self.start_time!r}, " f"end_time={self.end_time!r})"


class GlacierHistory:
    def __init__(self):
        self.mem_conn = sqlite3.connect(":memory:")
        self._init_db()
        self.ref_date = pd.Timestamp("1801-01-01")

    # ----------------------------
    # DB setup
    # ----------------------------
    def _init_db(self):
        cursor = self.mem_conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS glacier_change_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component TEXT,
                subcomponent TEXT,
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

        self.mem_conn.commit()

    # ----------------------------
    # Insert
    # ----------------------------
    def add_event(self, event: GlacierChangeEvent):

        start_time = (event.start_time - self.ref_date).days  # convert to days since ref for sql
        end_time = (event.end_time - self.ref_date).days  # convert to days since ref for sql

        cursor = self.mem_conn.cursor()

        blob = self.array_to_blob(event.change)

        cursor.execute(
            """
            INSERT INTO glacier_change_events
            (component, subcomponent, field, change, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (event.component.__class__.__name__, event.subcomponent, event.field, blob, start_time, end_time),
        )

        self.mem_conn.commit()

    def mem_to_disk(self):
        # Store the glacier changes on disk (possibly optional)

        if os.path.exists("glacier_history.db"):
            os.remove("glacier_history.db")

        # create disk database
        disk_conn = sqlite3.connect("glacier_history.db")

        # copy everything from memory → disk
        self.mem_conn.backup(disk_conn)

        disk_conn.close()

    # ----------------------------
    # Close db memory connection
    # ----------------------------
    def close(self):
        self.mem_conn.close()

    # ----------------------------
    # Array <-> BLOB helpers
    # ----------------------------
    @staticmethod
    def array_to_blob(arr: np.ndarray) -> bytes:
        buffer = io.BytesIO()
        np.save(buffer, arr)
        return buffer.getvalue()

    def blob_to_array(self, blob: bytes) -> np.ndarray:
        buffer = io.BytesIO(blob)
        buffer.seek(0)
        return np.load(buffer)

    # Query functions

    def aggregate_change(self, component: str, field: str, start_time: pd.Timestamp, end_time: pd.Timestamp):
        cursor = self.mem_conn.cursor()

        start_time = (start_time - self.ref_date).days  # convert to days since ref for sql
        end_time = (end_time - self.ref_date).days  # convert to days since ref for sql

        cursor.execute(
            """
            SELECT change
            FROM glacier_change_events
            WHERE component = ?
            AND field = ?
            AND start_time >= ?
            AND end_time <= ?
            """,
            (component, field, start_time, end_time),
        )

        total = None

        for (blob,) in cursor:
            arr = self.blob_to_array(blob)

            if total is None:
                total = arr.copy()
            else:
                total += arr

        return total
