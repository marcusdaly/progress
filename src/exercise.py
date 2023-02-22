import os
from datetime import datetime
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm

from config import get_activity_vault
from dir_utils import get_activity_dir, get_practices_dir
from plan import _filter_non_digits, _measurement_to_metric


def _get_exercises_from_file(session_dir: str) -> List[str]:
    with open(session_dir, "r") as file:
        lines = file.readlines()

    for line_idx, line in enumerate(lines):
        if line == "## Notes\n":
            lines = lines[:line_idx]
            break
    exercises_lines = [line[2:].strip() for line in lines if line.startswith("- ")]
    exercises_lines = [
        line[4:] if line.startswith("[") else line for line in exercises_lines
    ]

    exercises_lines = [
        line[:-9].strip() if line.endswith("- SKIPPED") else line
        for line in exercises_lines
    ]
    exercises_lines = [line for line in exercises_lines if len(line) > 0]

    return exercises_lines


def _get_exercise_results_from_file(
    session_dir: str, exercise_name: str
) -> Tuple[datetime, dict]:
    found_exercise = False
    session_name = session_dir.split("/")[-1][:-3].split("-")[-1].strip()
    session_date_str = session_dir.split("/")[-1][:10]
    session_date = datetime.strptime(session_date_str, "%Y-%m-%d")
    exercise_results = {}
    with open(session_dir, "r") as file:
        lines = file.readlines()

    metrics = None
    for line in lines:
        if line.startswith("## Notes"):
            break
        if line.startswith("# "):
            skipped = "skipped" in line.lower()
            exercise_results["skipped"] = skipped
            if skipped:
                break

            # assert line[2:-1] == session_name, f"{line[2:-1]} != {session_name}"

        elif line.startswith("- "):
            completion_false = line.startswith("- [ ] ")
            completion_true = line.startswith("- [x] ")
            new_exercise_name = (
                line[6:-1] if completion_false or completion_true else line[2:-1]
            )
            if found_exercise:
                return session_date, exercise_results
            if new_exercise_name == exercise_name:
                found_exercise = True
                exercise_results = {}
                if completion_false:
                    exercise_results["completed"] = False
                if completion_true:
                    exercise_results["completed"] = True

        elif line.startswith("\t- "):
            if line[3:].startswith("Metric: "):
                metrics = [metric.strip() for metric in line[11:].split("|")]
                if "completed" not in exercise_results:
                    for metric in metrics:
                        exercise_results[metric] = []

        elif line.startswith("\t") and len(line) >= 3 and line[2] == ".":
            set_num = int(line[1])
            set_measurements = [
                measurement.strip() for measurement in line[3:].split(",")
            ]
            set_metrics = [
                _measurement_to_metric(measurement) for measurement in set_measurements
            ]
                
            for metric, measurement in zip(set_metrics, set_measurements):
                if "Hours" == metric and "Minutes" in set_metrics:
                    measurement_val = _filter_non_digits(measurement)
                    new_measurement_val = float(measurement_val) + int(_filter_non_digits(set_measurements[set_metrics.index("Minutes")])) / 60
                    measurement = f"{new_measurement_val}{measurement.removeprefix(measurement_val)}"
                
                if "Minutes" == metric and "Hours" in set_metrics:
                    continue

                if metric in exercise_results:
                    exercise_results[metric].append(measurement)

    if not found_exercise:
        return session_date, {}
    return session_date, exercise_results


def get_exercises(activity: str,) -> List[str]:
    practices_dir = get_practices_dir(activity=activity)
    if not os.path.isdir(practices_dir):
        raise ValueError(practices_dir)

    all_session_exercises = []
    for session in os.listdir(practices_dir):
        session_dir = f"{practices_dir}/{session}"
        # extract exercises from session plan
        print(session)
        session_exercises = _get_exercises_from_file(session_dir)
        all_session_exercises.extend(session_exercises)

    return list(set(all_session_exercises))


def get_exercise(activity: str, exercise: str, start: Optional[str] = None):
    if start is not None:
        start = datetime.strptime(start, "%Y-%m-%d")
    practices_dir = get_practices_dir(activity=activity)
    if not os.path.isdir(practices_dir):
        raise ValueError(practices_dir)

    all_session_exercises = []
    session_dates = []
    for session in os.listdir(practices_dir):
        session_dir = f"{practices_dir}/{session}"
        # extract exercises from session plan
        session_date, session_exercises = _get_exercise_results_from_file(
            session_dir, exercise_name=exercise
        )
        if len(session_exercises) > 0:
            all_session_exercises.append(session_exercises)
            session_dates.append(session_date)
    print(all_session_exercises)
    metrics = list(
        set(
            [
                key
                for exercise_metrics in all_session_exercises
                for key in exercise_metrics
            ]
        )
    )
    print(metrics)
    for metric in metrics:
        date_and_measurements = [
            (date, exercise_metrics[metric])
            for date, exercise_metrics in zip(session_dates, all_session_exercises)
        ]

        # filter by date
        if start is not None:
            date_and_measurements = [
                (date, measurement)
                for date, measurement in date_and_measurements
                if date >= start
            ]

        # take just first for now
        print(date_and_measurements)
        date_and_measurements = [
            (
                date,
                max(
                    [
                        float(_filter_non_digits(set_measurement))
                        for set_measurement in measurement
                    ]
                ),
            )
            if len(measurement) > 0 and any(len(m) > 0 for m in measurement)
            else (date, np.nan)
            for date, measurement in date_and_measurements
        ]
        dates = [date for date, _ in date_and_measurements]
        measurements = [measurement for _, measurement in date_and_measurements]
        data = pd.DataFrame(
            {
                "Session": np.arange(len(measurements)),
                "Date": dates,
                metric: np.array(measurements),
            }
        )
        print(measurements)

        y = np.array(measurements)
        x = np.arange(len(y))
        notnan_indices = np.argwhere(~np.isnan(y))
        y = y[notnan_indices]
        x = x[notnan_indices]
        if y.shape[0] == 0:
            print("skipping", metric)
            continue
        print(x, y)
        model = sm.OLS(y, sm.add_constant(x))
        result = model.fit()
        print(result.summary())
        # plt.plot(np.arange(len(measurements)), measurements)
        ax = sns.lmplot(data=data, x="Session", y=metric, height=8, aspect=1.4)
        plt.show()
        ax = sns.scatterplot(data=data, x="Date", y=metric)
        plt.show()
    return session_exercises
