import json
import sqlite3
from pathlib import Path

# Database connection
def get_db_connection():
    connection = sqlite3.connect(Path("backend/data/passes.db"))
    connection.row_factory = sqlite3.Row
    return connection

# Load flight plan data from JSON file
def _import_flightplan_from_json():
    json_path=Path("backend/data/flight_plan.json")
    
    with open(json_path, "r") as file:
        flight_plan = json.load(file)

    return flight_plan

# Create tables for selected and rejected passes
def _create_tables():
    connection = get_db_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS selected_passes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pass_id TEXT NOT NULL,
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
            pass_id TEXT NOT NULL,
            rejection_reason TEXT NOT NULL,
            details TEXT
        )
        """
    )
    connection.commit()
    connection.close()

# Insert selected passes into the database
def _insert_into_selected_passes():
    connection = get_db_connection()
    flight_plan = _import_flightplan_from_json()
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
        INSERT INTO selected_passes (pass_id, station_id, start_time, end_time, downlink_mb, priority_score)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        values,
    )
    connection.commit()
    connection.close()

# Insert rejected passes into the database
def _insert_into_rejected_passes():
    connection = get_db_connection()
    flight_plan = _import_flightplan_from_json()
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
        INSERT INTO rejected_passes (pass_id, rejection_reason, details)
        VALUES (?, ?, ?)
        """,
        values,
    )
    connection.commit()
    connection.close()
    
def read_selectpass_from_id(id):
    connection = get_db_connection()
    selected_rows = connection.execute(
        "SELECT * FROM selected_passes WHERE id = ?",
        (id,)
    ).fetchall()
    selected_passes = [dict(row) for row in selected_rows]
    connection.close()
    return selected_passes

def read_rejectpass_from_id(id):
    connection = get_db_connection()
    rejected_rows = connection.execute(
        "SELECT * FROM rejected_passes WHERE id = ?",
        (id,)
    ).fetchall()
    rejected_passes = [dict(row) for row in rejected_rows]
    connection.close()
    return rejected_passes

# Run scheduling
def initialize_database():
    _create_tables()
    
def run_schedule():
    _create_tables()
    _insert_into_selected_passes()
    _insert_into_rejected_passes()
    
    
# get the maximum ID from the selected_passes table to identify the latest schedule
def get_max_id():
    connection = get_db_connection()
    selected_max = connection.execute(
        "SELECT MAX(id) FROM selected_passes"
    ).fetchone()[0]

    rejected_max = connection.execute(
        "SELECT MAX(id) FROM rejected_passes"
    ).fetchone()[0]

    if selected_max is None:
        selected_max = 0

    if rejected_max is None:
        rejected_max = 0

    max_id = max(selected_max, rejected_max)
    connection.close()
    return max_id

# Get the latest schedule by fetching the maximum ID from the selected_passes table and retrieving the corresponding selected and rejected passes
def get_latest_schedule():
    max_id = get_max_id()
    selected_passes = read_selectpass_from_id(max_id)
    rejected_passes = read_rejectpass_from_id(max_id)

    total_downlink_mb = 0
    for selected_pass in selected_passes:
        total_downlink_mb = total_downlink_mb + selected_pass["downlink_mb"]

    total_selected_count = len(selected_passes)

    return {
        "selected_passes": selected_passes,
        "rejected_passes": rejected_passes,
        "total_downlink_mb": total_downlink_mb,
        "total_selected_count": total_selected_count
    }

def get_specific_schedule(id):
    selected_passes = read_selectpass_from_id(id)
    rejected_passes = read_rejectpass_from_id(id)

    total_downlink_mb = 0
    for selected_pass in selected_passes:
        total_downlink_mb = total_downlink_mb + selected_pass["downlink_mb"]

    total_selected_count = len(selected_passes)

    return {
        "selected_passes": selected_passes,
        "rejected_passes": rejected_passes,
        "total_downlink_mb": total_downlink_mb,
        "total_selected_count": total_selected_count
    }

# not needed since we will use fastapi to insert data into the database, but we can use it to initialize the database with the flight plan data
# connection = sqlite3.connect("backend/data/passes.db")
# _create_tables(connection)
# _insert_into_selected_passes(connection)
# _insert_into_rejected_passes(connection)

# connection.commit()
# connection.close()
