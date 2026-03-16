"""
Individual Lab 4 — Scheduling & Flight Plan

You must:
- Apply all constraints
- Implement one decision rule
- Produce flight_plan.json
"""

import json
from datetime import datetime

MIN_DURATION_MINUTES = 8
MAX_PASSES_PER_DAY = 3


def parse_time(ts):
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")


def duration_minutes(start, end):
    return (end - start).total_seconds() / 60


def load_passes(filename):
    with open(filename, "r") as f:
        data = json.load(f)

    # TODO:
    # Return satellite_id, date, and passes
    return data["satellite_id"], data["date"], data["passes"]


def filter_valid_passes(passes):
    """
    You must:
    - Reject passes where end <= start
    - Reject passes with duration < MIN_DURATION_MINUTES
    """

    valid = []

    # TODO:


    # Implement filtering logic here

    for p in passes:
        start = parse_time(p["start_time"])
        end = parse_time(p["end_time"])

        # Reject if end <= start
        if end <= start:
            continue

        # Reject if duration < MIN_DURATION_MINUTES
        dur = duration_minutes(start, end)
        if dur < MIN_DURATION_MINUTES:
            continue

        valid.append(p)

    return valid


def schedule_passes(passes):
    """
    You must:
    - Choose and implement ONE decision rule
    - Ensure no overlapping passes
    - Respect MAX_PASSES_PER_DAY
    """

    # Shortest duration first

    scheduled = []

    # TODO:
    # 1. Sort passes based on your decision rule
    scheduled = sorted(passes, key=lambda p: duration_minutes(parse_time(p["start_time"]), parse_time(p["end_time"])))
    non_overlapping = []
    # 2. Select non-overlapping passes
    for p in scheduled:
        start_p = parse_time(p["start_time"])
        end_p = parse_time(p["end_time"])

        # Check overlap med eksisterende passes
        overlap = False
        for s in non_overlapping:
            start_s = parse_time(s["start_time"])
            end_s = parse_time(s["end_time"])
            if start_p < end_s and end_p > start_s:
                overlap = True
                break

        if overlap:
            continue

        non_overlapping.append(p)

        if len(non_overlapping) == MAX_PASSES_PER_DAY:
            break

    return non_overlapping


def generate_flight_plan(satellite_id, date, scheduled_passes):
    """
    Output format must match specification.
    """
    dictionary = {}



    # TODO:
    # Return dictionary with:
    # {
    #   "satellite_id": ...,
    #   "date": ...,
    #   "scheduled_passes": [...]
    # }
    dictionary["satellite_id"] = satellite_id
    dictionary["date"] = date
    dictionary["scheduled_passes"] = scheduled_passes
    return dictionary


def main():
    satellite_id, date, passes = load_passes("official_passes.json")

    valid_passes = filter_valid_passes(passes)
    scheduled = schedule_passes(valid_passes)

    flight_plan = generate_flight_plan(
        satellite_id,
        date,
        scheduled
    )

    with open("flight_plan.json", "w") as f:
        json.dump(flight_plan, f, indent=2)

    print("Flight plan generated.")


if __name__ == "__main__":
    main()

