"""
Individual Lab 5 - Scheduling & Flight Plan

You must:
- Apply all constraints
- Implement one decision rule
- Produce flight_plan.json
"""

import json
from datetime import datetime


def parse_time(time_text):
    # turn text into a datetime
    return datetime.strptime(time_text, "%Y-%m-%dT%H:%M:%S")


def duration_minutes(start_time, end_time):
    # change seconds into minutes
    seconds = (end_time - start_time).total_seconds()
    return seconds / 60


def load_passes(filename):
    # read the passes file
    with open(filename, "r") as file:
        data = json.load(file)
    return data["passes"]


def load_policies(filename):
    # read the policy file
    with open(filename, "r") as file:
        data = json.load(file)
    return data


def pass_sort_key(single_pass):
    # sort by priority then time then id
    priority = -single_pass["priority_score"]
    start_time = single_pass["start_time"]
    pass_id = single_pass["pass_id"]
    return (priority, start_time, pass_id)


def sort_passes(passes):
    # use the rule order for sorting
    return sorted(passes, key=pass_sort_key)


def passes_overlap(first_pass, second_pass):
    # check if the time windows overlap
    first_start = parse_time(first_pass["start_time"])
    first_end = parse_time(first_pass["end_time"])
    second_start = parse_time(second_pass["start_time"])
    second_end = parse_time(second_pass["end_time"])

    return first_start < second_end and second_start < first_end


def spacing_between_passes(first_pass, second_pass):
    # find the gap between two passes
    first_start = parse_time(first_pass["start_time"])
    first_end = parse_time(first_pass["end_time"])
    second_start = parse_time(second_pass["start_time"])
    second_end = parse_time(second_pass["end_time"])

    if first_end <= second_start:
        return duration_minutes(first_end, second_start)

    return duration_minutes(second_end, first_start)


def check_time_window(single_pass):
    # make sure the pass has a real time window
    start_time = parse_time(single_pass["start_time"])
    end_time = parse_time(single_pass["end_time"])

    if end_time > start_time:
        return None

    return {
        "pass_id": single_pass["pass_id"],
        "rejection_reason": "INVALID_TIME_WINDOW",
        "details": "end_time must be later than start_time",
    }


def check_capacity_constraint(current_pass, selected_passes, policies):
    # get station and antenna limit
    station_id = current_pass["station_id"]
    antenna_limits = policies.get("antenna_count_by_station", {})
    antenna_limit = antenna_limits.get(station_id, 0)

    # store ids that overlap
    conflicting_pass_ids = []

    for selected_pass in selected_passes:
        if selected_pass["station_id"] != station_id: # check only passes for the same station
            continue

        if passes_overlap(current_pass, selected_pass):
            conflicting_pass_ids.append(selected_pass["pass_id"])

    if len(conflicting_pass_ids) < antenna_limit:
        return None

    # reject if the station is full
    return {
        "pass_id": current_pass["pass_id"],
        "rejection_reason": "CAPACITY_CONFLICT",
        "details": (
            "station_id="
            + station_id
            + ", antenna_limit="
            + str(antenna_limit)
            + ", conflicting_passes="
            + ", ".join(conflicting_pass_ids)
        ),
    }


def check_spacing_constraint(current_pass, selected_passes, policies):
    # get the needed spacing for this station
    station_id = current_pass["station_id"]
    min_spacing_by_station = policies.get("min_spacing_minutes_by_station", {})
    min_spacing = min_spacing_by_station.get(station_id, 0)

    for selected_pass in selected_passes:
        if selected_pass["station_id"] != station_id:
            continue

        if passes_overlap(current_pass, selected_pass):
            continue

        # check the time gap
        gap_minutes = spacing_between_passes(current_pass, selected_pass)

        if gap_minutes < min_spacing:
            # reject if the gap is too small
            return {
                "pass_id": current_pass["pass_id"],
                "rejection_reason": "SPACING_VIOLATION",
                "details": (
                    "station_id="
                    + station_id
                    + ", required_spacing_minutes="
                    + str(min_spacing)
                    + ", conflicting_pass_id="
                    + selected_pass["pass_id"]
                    + ", actual_gap_minutes="
                    + str(gap_minutes)
                ),
            }

    return None


def check_budget_constraint(current_pass, used_budget, policies):
    # add this pass to the current budget
    max_budget = policies.get("max_downlink_mb_per_day", 0)
    projected_budget = used_budget + current_pass["downlink_mb"]

    if projected_budget <= max_budget:
        return None

    # reject if it goes over the budget
    return {
        "pass_id": current_pass["pass_id"],
        "rejection_reason": "BUDGET_EXCEEDED",
        "details": (
            "used_budget_mb="
            + str(used_budget)
            + ", pass_downlink_mb="
            + str(current_pass["downlink_mb"])
            + ", projected_budget_mb="
            + str(projected_budget)
            + ", max_budget_mb="
            + str(max_budget)
        ),
    }


def check_max_passes_constraint(current_pass, selected_passes, policies):
    # count how many are already selected
    max_passes = policies.get("max_passes_per_day", 0)
    selected_count = len(selected_passes)

    if selected_count < max_passes:
        return None

    # reject if the daily limit is reached
    return {
        "pass_id": current_pass["pass_id"],
        "rejection_reason": "MAX_PASSES_LIMIT",
        "details": (
            "selected_pass_count="
            + str(selected_count)
            + ", max_passes_per_day="
            + str(max_passes)
        ),
    }


def validate_passes(passes):
    # remove passes with invalid times
    valid_passes = []
    rejected_passes = []

    for single_pass in passes:
        rejection = check_time_window(single_pass)

        if rejection is None:
            valid_passes.append(single_pass)
        else:
            rejected_passes.append(rejection)

    return valid_passes, rejected_passes


def filter_valid_passes(passes, policies):
    # sort first before checking rules
    valid_passes, rejected_passes = validate_passes(passes)
    sorted_passes = sort_passes(valid_passes)

    selected_passes = []
    used_budget = 0

    for current_pass in sorted_passes:
        # rule 1 capacity
        rejection = check_capacity_constraint(current_pass, selected_passes, policies)
        if rejection is not None:
            rejected_passes.append(rejection)
            continue

        # rule 2 spacing
        rejection = check_spacing_constraint(current_pass, selected_passes, policies)
        if rejection is not None:
            rejected_passes.append(rejection)
            continue

        # rule 3 budget
        rejection = check_budget_constraint(current_pass, used_budget, policies)
        if rejection is not None:
            rejected_passes.append(rejection)
            continue

        # rule 4 max passes
        rejection = check_max_passes_constraint(current_pass, selected_passes, policies)
        if rejection is not None:
            rejected_passes.append(rejection)
            continue

        # keep the pass if all rules are ok
        selected_passes.append(current_pass)
        used_budget = used_budget + current_pass["downlink_mb"]

    return selected_passes, rejected_passes


def total_downlink(selected_passes):
    # add all selected downlink values
    total = 0

    for single_pass in selected_passes:
        total = total + single_pass["downlink_mb"]

    return total


def generate_flight_plan(selected_passes, rejected_passes):
    # build the final output data
    return {
        "selected_passes": selected_passes,
        "rejected_passes": rejected_passes,
        "total_downlink_mb": total_downlink(selected_passes),
        "total_selected_count": len(selected_passes),
    }


def count_rejection_reasons(rejected_passes):
    # count each rejection type
    counts = {}

    for rejected_pass in rejected_passes:
        reason = rejected_pass["rejection_reason"]

        if reason not in counts:
            counts[reason] = 0

        counts[reason] = counts[reason] + 1

    return counts


def print_pass_summary(flight_plan):
    # print a small summary
    print("SELECTED:", flight_plan["total_selected_count"])

    rejection_counts = count_rejection_reasons(flight_plan["rejected_passes"])

    for reason in sorted(rejection_counts):
        print(reason + ":", rejection_counts[reason])


def main():
    # load the input files
    passes = load_passes("lab5/input1_passes_medium.json")
    policies = load_policies("lab5/input1_policies_medium.json")

    # run the scheduler
    selected_passes, rejected_passes = filter_valid_passes(passes, policies)
    flight_plan = generate_flight_plan(selected_passes, rejected_passes)

    # save the result
    with open("lab5/flight_plan.json", "w") as file:
        json.dump(flight_plan, file, indent=2)

    print("Flight plan generated.")
    print_pass_summary(flight_plan)


if __name__ == "__main__":
    main()
