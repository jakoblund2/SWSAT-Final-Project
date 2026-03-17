import json
import sqlite3
from datetime import datetime
from pathlib import Path


DEFAULT_DB_PATH = Path("backend/data/passes.db")

# Create database
sqlite3.connect(DEFAULT_DB_PATH).close()


def import_flightplan_from_json():
    json_path=Path("backend/data/flight_plan.json")
    db_path=DEFAULT_DB_PATH

    with open(json_path, "r") as file:
        flight_plan = json.load(file)

    return flight_plan


def _create_tables(connection):    
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS selected_passes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pass_id TEXT NOT NULL UNIQUE,
            station_id TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            downlink_mb REAL NOT NULL,
            priority_score INTEGER NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS rejected_passes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pass_id TEXT NOT NULL UNIQUE,
            rejection_reason TEXT NOT NULL,
            details TEXT
        )
        """
    )

def _insert_into_selected_passes(connection):
    flight_plan = import_flightplan_from_json()
    values = [
        (
            selected_pass["pass_id"],
            selected_pass["station_id"],
            selected_pass["start_time"],
            selected_pass["end_time"],
            selected_pass["downlink_mb"],
            selected_pass["priority_score"],
        )
        for selected_pass in flight_plan["selected_passes"]
    ]
    connection.executemany(
        """
        INSERT OR IGNORE INTO selected_passes (pass_id, station_id, start_time, end_time, downlink_mb, priority_score)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        values,
    )

def _insert_into_rejected_passes(connection):
    flight_plan = import_flightplan_from_json()
    values = [
        (
            rejected_pass["pass_id"],
            rejected_pass["rejection_reason"],
            rejected_pass["details"]
        )
        for rejected_pass in flight_plan["rejected_passes"]
    ]
    connection.executemany(
        """
        INSERT OR IGNORE INTO rejected_passes (pass_id, rejection_reason, details)
        VALUES (?, ?, ?)
        """,
        values,
    )

connection = sqlite3.connect("backend/data/passes.db")

# _create_tables(connection)
# _insert_into_selected_passes(connection)
# _insert_into_rejected_passes(connection)

# connection.commit()
# connection.close()