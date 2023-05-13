import datetime
import os
from typing import List

import matplotlib.pyplot as plt
import numpy as np

from dir_utils import get_activity_dir, get_plan_dir, get_practices_dir
from practice import create_practice
from units import (
    HOURS_UNITS,
    LEFT_UNITS,
    MINUTES_UNITS,
    POUNDS_UNITS,
    PERCENTAGE_UNITS,
    RIGHT_UNITS,
    SECONDS_UNITS,
    combine_units,
)

DOW_TO_INT = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}


def create_plan(plan: str, activity: str):
    # add on date to activity name:
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    plan_dir = get_plan_dir(plan=plan, activity=activity, date=date)
    if os.path.isdir(plan_dir):
        raise ValueError(plan)
    os.mkdir(plan_dir)

    schedule_name = "Schedule.md"
    schedule_path = os.path.join(plan_dir, schedule_name)
    if os.path.isfile(schedule_path):
        raise ValueError(schedule_path)

    with open(schedule_path, "w") as file:
        file.write("# Monday\n")
        file.write("- SESSION TYPE\n")
        file.write("\t- (HH:MM - HH:MM)\n")
        file.write("# Tuesday\n")
        file.write("- SESSION TYPE\n")
        file.write("\t- (HH:MM - HH:MM)\n")
        file.write("# Wednesday\n")
        file.write("- SESSION TYPE\n")
        file.write("\t- (HH:MM - HH:MM)\n")
        file.write("# Thursday\n")
        file.write("- SESSION TYPE\n")
        file.write("\t- (HH:MM - HH:MM)\n")
        file.write("# Friday\n")
        file.write("- SESSION TYPE\n")
        file.write("\t- (HH:MM - HH:MM)\n")
        file.write("# Saturday\n")
        file.write("- SESSION TYPE\n")
        file.write("\t- (HH:MM - HH:MM)\n")
        file.write("# Sunday\n")
        file.write("- SESSION TYPE\n")
        file.write("\t- (HH:MM - HH:MM)\n")


def schedule(until: str, plan: str, activity: str):
    until_date = datetime.datetime.strptime(until, "%Y-%m-%d")
    date = datetime.datetime.now()

    plan_dir = get_plan_dir(plan=plan, activity=activity)
    if not os.path.isdir(plan_dir):
        raise ValueError(plan)
    schedule_name = "Schedule.md"
    schedule_path = os.path.join(plan_dir, schedule_name)
    if not os.path.isfile(schedule_path):
        raise ValueError(schedule_path)

    with open(schedule_path, "r") as file:
        lines = file.readlines()

    dow_sessions = [[] for _ in range(7)]
    current_dow_sessions = []
    dow_index = None
    for line in lines:
        if line.startswith("# "):
            # new DoW, so done with last DoW
            if len(current_dow_sessions) > 0:
                dow_sessions[dow_index] = current_dow_sessions
                current_dow_sessions = []

            dow = line[2:-1].strip()
            dow_index = DOW_TO_INT[dow]
        elif line.startswith("- "):
            session_type = line.strip()[2:]
            if session_type != "Rest":
                current_dow_sessions.append({"Session Type": session_type})
        elif line.startswith("\t- "):
            times = line[3:-1]
            current_dow_sessions[-1]["Times"] = times

    # for last day, still may need to add the sessions.
    if len(current_dow_sessions) > 0:
        dow_sessions[dow_index] = current_dow_sessions

    while until_date > date:
        date_str = date.strftime("%Y-%m-%d")
        dow_index = date.weekday()

        # create practices for all sessions on this DoW
        # if multiple of same name, enumerate with numbers

        sessions = dow_sessions[dow_index]

        # before creating any, plan out their names.
        session_names = [
            " ".join([date_str, plan, "-", session["Session Type"]])
            for session in sessions
        ]

        # if need to enumerate, do so
        if list(set(session_names)) != session_names:
            # for each session that has multiple, append a number
            session_counts = {}
            for session_name in session_names:
                if session_name in session_counts:
                    session_counts[session_name] += 1
                else:
                    session_counts[session_name] = 1

            sessions_seen = {session_name: 0 for session_name in session_names}
            for session_idx, session_name in enumerate(session_names):
                if session_counts[session_name] > 1:
                    sessions_seen[session_name] += 1
                    session_names[
                        session_idx
                    ] = f"{session_name} {sessions_seen[session_name]}"

        # create the practices from the sessions
        for session, session_name in zip(sessions, session_names):
            print(session, session_name)
            create_practice(
                session_type=session["Session Type"],
                plan=plan,
                activity=activity,
                date=date_str,
                practice_name=session_name,
                error_if_exists=False,
            )

        date = date + datetime.timedelta(days=1)


def get_plans(activity: str) -> List[str]:
    activity_plan_dir = os.path.join(get_activity_dir(activity), "Plan")
    plan_paths = os.listdir(activity_plan_dir)
    plans = [
        path
        for path in plan_paths
        if os.path.isdir(os.path.join(activity_plan_dir, path))
        and not path.startswith(".")
    ]
    return plans


def _measurement_to_metric(measurement: str) -> str:
    lower_measurement = _filter_digits(measurement.lower()).strip()

    if lower_measurement in POUNDS_UNITS:
        return "Weight"
    if lower_measurement in combine_units(POUNDS_UNITS, RIGHT_UNITS):
        return "Weight Right"
    if lower_measurement in combine_units(POUNDS_UNITS, LEFT_UNITS):
        return "Weight Left"
    if lower_measurement in combine_units(SECONDS_UNITS, RIGHT_UNITS):
        return "Seconds Right"
    if lower_measurement in combine_units(SECONDS_UNITS, LEFT_UNITS):
        return "Seconds Left"
    if lower_measurement in RIGHT_UNITS:
        return "Reps Right"
    if lower_measurement in LEFT_UNITS:
        return "Reps Left"

    if lower_measurement in HOURS_UNITS:
        return "Hours"

    if lower_measurement in MINUTES_UNITS:
        return "Minutes"
    if lower_measurement in SECONDS_UNITS:
        return "Seconds"
    if lower_measurement in PERCENTAGE_UNITS:
        return "Percentage"
    if lower_measurement == "[x]" or lower_measurement == "[ ]":
        return "Completion"
    if lower_measurement == "planks":
        return "Distance"
    if lower_measurement == "":
        return "Reps"
    return "Variation"


def _filter_non_digits(string: str) -> str:
    result = ""
    for char in string:
        if char in "1234567890.":
            result += char
    return result


def _filter_digits(string: str) -> str:
    result = ""
    for char in string:
        if char not in "1234567890.":
            result += char
    return result


def visualize_plan(plan: str, activity: str):
    plan_dir = get_plan_dir(plan=plan, activity=activity)
    if not os.path.isdir(plan_dir):
        raise ValueError(plan)
    schedule_name = "Schedule.md"
    schedule_path = os.path.join(plan_dir, schedule_name)
    if not os.path.isfile(schedule_path):
        raise ValueError(schedule_path)

    # TODO get all of the sessions associated with this plan
    session_names = [
        file[:-3] for file in os.listdir(plan_dir) if file != schedule_name
    ]

    sessions = {session_name: [] for session_name in session_names}

    practices_dir = get_practices_dir(activity=activity)

    for practice_path, _, files in os.walk(practices_dir):
        for file in files:
            practice_name = file[:-3]
            split_practice_name = practice_name.split(" ")
            date = split_practice_name[0]
            session_name = " ".join(split_practice_name[3:])

            with open(os.path.join(practice_path, practice_name + ".md"), "r") as file:
                # extract exercises from practice
                practice_lines = file.readlines()

            sessions[session_name].append({})
            sessions[session_name][-1]["date"] = date

            if datetime.datetime.strptime(date, "%Y-%m-%d") > datetime.datetime.now():
                continue

            metrics = None

            for line in practice_lines:
                if line.startswith("## Notes"):
                    break
                if line.startswith("# "):
                    skipped = "skipped" in line.lower()
                    sessions[session_name][-1]["skipped"] = skipped
                    if skipped:
                        break

                    assert line[2:-1] == session_name, f"{line[2:-1]} != {session_name}"

                elif line.startswith("- "):
                    completion_false = line.startswith("- [ ] ")
                    completion_true = line.startswith("- [x] ")
                    exercise_name = (
                        line[6:-1]
                        if completion_false or completion_true
                        else line[2:-1]
                    )
                    sessions[session_name][-1][exercise_name] = {}
                    if completion_false:
                        sessions[session_name][-1][exercise_name]["completed"] = False
                    if completion_true:
                        sessions[session_name][-1][exercise_name]["completed"] = True

                elif line.startswith("\t- "):
                    if line[3:].startswith("Metric: "):
                        metrics = [metric.strip() for metric in line[11:].split("|")]
                        if "completed" not in sessions[session_name][-1][exercise_name]:
                            for metric in metrics:
                                sessions[session_name][-1][exercise_name][metric] = []

                elif line.startswith("\t") and len(line) >= 3 and line[2] == ".":
                    set_measurements = [
                        measurement.strip() for measurement in line[3:].split(",")
                    ]
                    set_metrics = [
                        _measurement_to_metric(measurement)
                        for measurement in set_measurements
                    ]
                    for metric, measurement in zip(set_metrics, set_measurements):
                        if metric in sessions[session_name][-1][exercise_name]:
                            sessions[session_name][-1][exercise_name][metric].append(
                                measurement
                            )

                    # if metrics is not None:
                    #     print(set_num, set_measurements, metrics)

    # print(sessions[session_name])

    for session_name in sessions:
        session_keys = set.union(
            *[set(session.keys()) for session in sessions[session_name]]
        )
        print(session_name)

        # for each, plot something
        for session_key in session_keys:
            if session_key == "date":
                continue
            # print(sessions)
            dated_vals = [
                (session["date"], session[session_key])
                for session in sessions[session_name]
                if session_key in session
            ]
            print(dated_vals)
            if len(dated_vals) > 0 and any(
                isinstance(dated_val[1], dict) and "Reps" in dated_val[1]
                for dated_val in dated_vals
            ):
                plt.plot_date(
                    [dated_val[0] for dated_val in dated_vals],
                    [
                        np.mean([int(reps) for reps in dated_val[1]["Reps"]])
                        if "Reps" in dated_val[1] and len(dated_val[1]["Reps"]) > 0
                        else 0
                        for dated_val in dated_vals
                    ],
                )
                plt.title(f"{session_key} Reps")
                plt.show()
            if len(dated_vals) > 0 and any(
                isinstance(dated_val[1], dict) and "Weight" in dated_val[1]
                for dated_val in dated_vals
            ):
                plt.plot_date(
                    [dated_val[0] for dated_val in dated_vals],
                    [
                        np.mean(
                            [
                                float(_filter_non_digits(weight))
                                for weight in dated_val[1]["Weight"]
                            ]
                        )
                        if "Weight" in dated_val[1] and len(dated_val[1]["Weight"]) > 0
                        else 0
                        for dated_val in dated_vals
                    ],
                )
                plt.title(f"{session_key} Weight")
                plt.show()
            if len(dated_vals) > 0 and any(
                isinstance(dated_val[1], bool) for dated_val in dated_vals
            ):
                plt.plot_date(
                    [dated_val[0] for dated_val in dated_vals],
                    [1 if dated_val[1] else 0 for dated_val in dated_vals],
                )
                plt.title(f"{session_name} {session_key}")
                plt.show()
