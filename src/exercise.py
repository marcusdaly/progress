import os
from datetime import datetime
from logging import debug
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm

from dir_utils import get_practices_dir
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
    session_date_str = os.path.split(session_dir)[-1][:10]
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
            set_measurements = [
                measurement.strip() for measurement in line[3:].split(",")
            ]
            set_metrics = [
                _measurement_to_metric(measurement) for measurement in set_measurements
            ]

            for metric, measurement in zip(set_metrics, set_measurements):
                if "Hours" == metric and "Minutes" in set_metrics:
                    measurement_val = _filter_non_digits(measurement)
                    new_measurement_val = (
                        float(measurement_val)
                        + int(
                            _filter_non_digits(
                                set_measurements[set_metrics.index("Minutes")]
                            )
                        )
                        / 60
                    )
                    measurement = (
                        f"{new_measurement_val}"
                        f"{measurement.removeprefix(measurement_val)}"
                    )

                if "Minutes" == metric and "Hours" in set_metrics:
                    continue

                if metric in exercise_results:
                    exercise_results[metric].append(measurement)

    if not found_exercise:
        return session_date, {}
    return session_date, exercise_results


def get_exercises(
    activity: str,
) -> List[str]:
    practices_dir = get_practices_dir(activity=activity)
    if not os.path.isdir(practices_dir):
        raise ValueError(practices_dir)

    all_session_exercises = []
    for session_path, _, files in os.walk(practices_dir):
        for session in files:
            session_dir = os.path.join(session_path, session)
            # extract exercises from session plan
            session_exercises = _get_exercises_from_file(session_dir)
            all_session_exercises.extend(session_exercises)

    return list(set(all_session_exercises))


def get_exercise(
    activity: str, exercise: str, start: Optional[str] = None
) -> Dict[str, pd.DataFrame]:
    if start is not None:
        start = datetime.strptime(start, "%Y-%m-%d")
    practices_dir = get_practices_dir(activity=activity)
    if not os.path.isdir(practices_dir):
        raise ValueError(practices_dir)

    all_session_exercises: List[Dict] = []
    session_dates = []
    for session_path, _, files in os.walk(practices_dir):
        for session in files:
            session_dir = os.path.join(session_path, session)
            # extract exercises from session plan
            session_date, session_exercises = _get_exercise_results_from_file(
                session_dir, exercise_name=exercise
            )
            if len(session_exercises) > 0:
                all_session_exercises.append(session_exercises)
                session_dates.append(session_date)
    metrics = list(
        set(
            [
                key
                for exercise_metrics in all_session_exercises
                for key in exercise_metrics
            ]
        )
    )

    all_data = {}
    for metric in metrics:
        date_and_measurements = [
            (date, exercise_metrics.get(metric, {}))
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
        date_and_measurements = [
            (
                date,
                max(
                    [
                        float(_filter_non_digits(set_measurement))
                        - (0 if print(date) is None else 0)
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
        exercise_metric = f"{exercise} ({metric})"
        data = pd.DataFrame(
            {
                "Session": np.arange(len(measurements)),
                "Date": dates,
                exercise_metric: np.array(measurements),
            }
        )

        y = np.array(measurements)
        notnan_indices = np.argwhere(~np.isnan(y))
        y = y[notnan_indices]
        if y.shape[0] == 0:
            debug("skipping", exercise_metric)
            continue

        all_data[exercise_metric] = data

    return all_data


def visualize_exercise_data(all_data: Dict[str, pd.DataFrame]):
    num_metrics = len(all_data)
    _, axs = plt.subplots(
        nrows=num_metrics, ncols=1, figsize=(20, num_metrics * 3), sharex="col"
    )

    if num_metrics == 1:
        axs = np.array([axs])

    for metric_idx, (metric, data) in enumerate(all_data.items()):

        print(f"Results for {metric}:")

        # Session-wise
        y = data[metric].to_numpy()
        x = data["Session"].to_numpy()
        notnan_indices = np.argwhere(~np.isnan(y)).flatten()
        y = y[notnan_indices]
        x = x[notnan_indices]
        model = sm.OLS(y, sm.add_constant(x))
        result = model.fit()

        debug(f"{metric} Rates\n")
        debug(result.summary())
        metric_per_session = result.params[1]
        print(f"Increase per Session: {metric_per_session:0.2f}")

        # Week-wise
        y = data[metric].to_numpy()
        weeks_from_start = (data["Date"] - data["Date"].iat[0]).dt.days / 7
        x = weeks_from_start.to_numpy()
        notnan_indices = np.argwhere(~np.isnan(y)).flatten()
        y = y[notnan_indices]
        x = x[notnan_indices]
        model = sm.OLS(y, sm.add_constant(x))
        result = model.fit()

        debug(f"{metric} Week-wise\n")
        debug(result.summary())
        base_metric = result.params[0]
        metric_per_week = result.params[1]
        print(f"Increase per Week: {metric_per_week:0.2f}\n")
        data = data.iloc[notnan_indices, :]

        sns.scatterplot(data=data, x="Date", y=metric, ax=axs[metric_idx])
        axs[metric_idx].plot(data["Date"], base_metric + metric_per_week * x)

        # Predictions
        print(f"{metric} Predictions:")
        week_4_pred = base_metric + metric_per_week * (x[-1] + 4)
        print(f"1 Month (4 Weeks): {week_4_pred:0.2f}")
        week_13_pred = base_metric + metric_per_week * (x[-1] + 13)
        print(f"1 Season (13 Weeks): {week_13_pred:0.2f}")
        week_26_pred = base_metric + metric_per_week * (x[-1] + 26)
        print(f"1/2 Year (26 Weeks): {week_26_pred:0.2f}")
        week_52_pred = base_metric + metric_per_week * (x[-1] + 52)
        print(f"1 Year (52 Weeks): {week_52_pred:0.2f}")

        if metric_idx != num_metrics - 1:
            print("\n")
    plt.tight_layout()
    plt.show()
