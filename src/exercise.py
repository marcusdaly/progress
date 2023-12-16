import os
from datetime import datetime
from logging import debug
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm

from dir_utils import get_practices_dir
from plan import _filter_non_digits, _measurement_to_metric, _str_to_float

plt.style.use("seaborn-v0_8")


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


def _handle_metric(line: str, exercise_results: Dict[str, Any]):
    if line[3:].startswith("Metric: "):
        metrics = [metric.strip() for metric in line[11:].split("|")]
        if "completed" not in exercise_results:
            for metric in metrics:
                exercise_results[metric] = []


def _handle_set(line: str, exercise_results: Dict[str, Any]):
    set_measurements = [measurement.strip() for measurement in line[3:].split(",")]
    set_metrics = [
        _measurement_to_metric(measurement) for measurement in set_measurements
    ]

    for metric, measurement in zip(set_metrics, set_measurements):
        if "Hours" == metric and "Minutes" in set_metrics:
            measurement_val = _filter_non_digits(measurement)
            new_measurement_val = (
                float(measurement_val)
                + int(
                    _filter_non_digits(set_measurements[set_metrics.index("Minutes")])
                )
                / 60
            )
            measurement = (
                f"{new_measurement_val}" f"{measurement.removeprefix(measurement_val)}"
            )

        if "Minutes" == metric and "Hours" in set_metrics:
            continue

        if metric in exercise_results:
            exercise_results[metric].append(measurement)


def _handle_exercise(
    line: str,
    exercise_results: Dict[str, Any],
    exercise_name: str,
) -> bool:
    found_exercise = False
    completion_false = line.startswith("- [ ] ")
    completion_true = line.startswith("- [x] ")
    new_exercise_name = (
        line[6:-1] if completion_false or completion_true else line[2:-1]
    )
    if new_exercise_name == exercise_name:
        found_exercise = True
        exercise_results.clear()
        if completion_false:
            exercise_results["completed"] = False
        if completion_true:
            exercise_results["completed"] = True
    return found_exercise


def _get_exercise_results_from_file(
    session_dir: str, exercise_name: str
) -> Tuple[datetime, dict]:
    found_exercise = False
    session_date_str = os.path.split(session_dir)[-1][:10]
    session_date = datetime.strptime(session_date_str, "%Y-%m-%d")
    exercise_results = {}
    with open(session_dir, "r") as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith("## Notes"):
            break
        if line.startswith("# "):
            skipped = "skipped" in line.lower()
            exercise_results["skipped"] = skipped
            if skipped:
                break

        elif line.startswith("- "):
            if found_exercise:
                # We've made it to the next exercise, so we're done!
                return session_date, exercise_results
            found_exercise = _handle_exercise(line, exercise_results, exercise_name)

        elif line.startswith("\t- "):
            _handle_metric(line, exercise_results)

        elif line.startswith("\t") and len(line) >= 3 and line[2] == ".":
            _handle_set(line, exercise_results)

    if not found_exercise:
        return session_date, {}
    return session_date, exercise_results


def get_exercises(
    activity: str,
) -> List[str]:
    practices_dir = get_practices_dir(activity=activity)
    if not os.path.isdir(practices_dir):
        raise FileNotFoundError(practices_dir)

    all_session_exercises = []
    for session_path, _, files in os.walk(practices_dir):
        for session in files:
            session_dir = os.path.join(session_path, session)
            # extract exercises from session plan
            session_exercises = _get_exercises_from_file(session_dir)
            all_session_exercises.extend(session_exercises)

    return list(set(all_session_exercises))


def get_exercise(
    activity: str,
    exercise: str,
    start: Optional[str] = None,
) -> pd.DataFrame:
    """
    Get the data for a given exercise.

    Args:
        activity (str): The activity of the exercise.
        exercise (str): The specified exercise.
        start (Optional[str], optional): The date to start looking at historical data.
            Defaults to None.

    Returns:
        pd.DataFrame: A dataframe of the results.
            This has the following columns:
            - Date
            - Session
            - Set
            - One column corresponding to each metric.
            Each row corresponds to a single set performed.
    """
    if start is not None:
        start = datetime.strptime(start, "%Y-%m-%d")
    practices_dir = get_practices_dir(activity=activity)
    if not os.path.isdir(practices_dir):
        raise FileNotFoundError(practices_dir)

    all_session_exercises: List[Dict] = []
    session_dates = []
    for session_path, _, files in os.walk(practices_dir):
        for session in files:
            session_dir = os.path.join(session_path, session)
            # extract exercises from session plan
            session_date, session_exercises = _get_exercise_results_from_file(
                session_dir, exercise_name=exercise
            )
            if len(session_exercises) > 0 and (start is None or session_date >= start):
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

        # take all measurements across all sets.
        date_and_measurements = [
            (
                date,
                [
                    _str_to_float(_filter_non_digits(set_measurement))
                    for set_measurement in measurement
                ],
            )
            if len(measurement) > 0 and any(len(m) > 0 for m in measurement)
            else (date, [np.nan])
            for date, measurement in date_and_measurements
        ]

        data = pd.DataFrame.from_records(
            [
                {
                    "Session": session_idx,
                    "Set": set_idx,
                    "Date": date,
                    metric: set_metric,
                }
                for session_idx, (date, measurements) in enumerate(
                    date_and_measurements
                )
                for set_idx, set_metric in enumerate(measurements)
            ]
        )

        y = data[metric].to_numpy()
        notnan_indices = np.argwhere(~np.isnan(y))
        if y[notnan_indices].shape[0] == 0:
            debug("skipping", exercise, metric)
            continue

        all_data[metric] = data

    final_metrics = list(all_data.keys())
    exercise_data = all_data[final_metrics[0]]
    for metric in final_metrics[1:]:
        exercise_data = pd.merge(
            exercise_data, all_data[metric], how="outer", on=["Date", "Set", "Session"]
        )

    # drop data if any rows are absent of measurements
    exercise_data = exercise_data.dropna(how="all", subset=final_metrics)

    return exercise_data


def visualize_exercise_data(
    all_data: Dict[str, pd.DataFrame], filename: Optional[str] = None
) -> Dict[str, Dict[str, Dict[str, float]]]:
    num_metrics = len(
        [
            col
            for data in all_data.values()
            for col in data.columns
            if col not in {"Set", "Date", "Session"}
        ]
    )
    _, axs = plt.subplots(
        nrows=num_metrics, ncols=1, figsize=(20, num_metrics * 3), sharex="col"
    )

    if num_metrics == 1:
        axs = np.array([axs])

    results_dict = {}

    num_plots = 0
    for exercise, data in sorted(all_data.items(), key=lambda x: x[0]):

        for metric in sorted(
            [col for col in data.columns if col not in {"Set", "Date", "Session"}]
        ):

            exercise_metric = f"{exercise} ({metric})"

            print(f"Results for {exercise_metric}:")

            # Session-wise
            y = data[metric].to_numpy()
            x = data["Session"].to_numpy()
            notnan_indices = np.argwhere(~np.isnan(y)).flatten()
            y = y[notnan_indices]
            x = x[notnan_indices]
            model = sm.OLS(y, sm.add_constant(x))
            result = model.fit()

            debug(f"{exercise_metric} Rates\n")
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

            debug(f"{exercise_metric} Week-wise\n")
            debug(result.summary())
            base_metric = result.params[0]
            metric_per_week = result.params[1]
            print(f"Increase per Week: {metric_per_week:0.2f}\n")
            notnan_data = data.iloc[notnan_indices, :]

            sns.scatterplot(data=notnan_data, x="Date", y=metric, ax=axs[num_plots])

            next_week = np.floor(np.max(x)) + 1
            max_forecast_weeks = 52
            # predict at most half as many weeks as we have observed
            num_forecast_weeks = min(max_forecast_weeks, (next_week - 1) // 2)
            final_week = next_week + num_forecast_weeks
            future_weeks_from_start = np.concatenate(
                [[np.max(x)], np.arange(next_week, final_week)]
            )
            dates_future = (
                notnan_data["Date"].iat[0]
                + pd.Timedelta(weeks=1) * future_weeks_from_start
            )
            plots = axs[num_plots].plot(
                notnan_data["Date"], base_metric + metric_per_week * x
            )
            axs[num_plots].plot(
                dates_future,
                base_metric + metric_per_week * future_weeks_from_start,
                linestyle="--",
                color=plots[-1].get_color(),
            )

            max_index = np.argmax(notnan_data[metric])
            axs[num_plots].axhline(
                notnan_data[metric].iat[max_index], c="tab:red", ls=":"
            )
            axs[num_plots].scatter(
                notnan_data["Date"].iat[max_index],
                notnan_data[metric].iat[max_index],
                c="tab:red",
            )

            exercise_metric_multiline = exercise_metric.replace(" (", "\n")
            exercise_metric_multiline = exercise_metric_multiline.replace(")", "")
            axs[num_plots].set_ylabel(exercise_metric_multiline)

            # Predictions
            print(f"{exercise_metric} Predictions:")
            week_4_pred = base_metric + metric_per_week * (x[-1] + 4)
            print(f"1 Month (4 Weeks): {week_4_pred:0.2f}")
            week_13_pred = base_metric + metric_per_week * (x[-1] + 13)
            print(f"1 Season (13 Weeks): {week_13_pred:0.2f}")
            week_26_pred = base_metric + metric_per_week * (x[-1] + 26)
            print(f"1/2 Year (26 Weeks): {week_26_pred:0.2f}")
            week_52_pred = base_metric + metric_per_week * (x[-1] + 52)
            print(f"1 Year (52 Weeks): {week_52_pred:0.2f}")

            results_dict[exercise_metric] = {
                "Rates": {
                    "Increase per Session": metric_per_session,
                    "Increase per Week": metric_per_week,
                },
                "Predictions": {
                    "1 Month (4 Weeks)": week_4_pred,
                    "1 Season (13 Weeks)": week_13_pred,
                    "1/2 Year (26 Weeks)": week_26_pred,
                    "1 Year (52 Weeks)": week_52_pred,
                },
            }

            if num_plots != num_metrics - 1:
                print("\n")

            num_plots += 1
    plt.tight_layout()
    if filename is None:
        plt.show()
    else:
        plt.savefig(filename)

    return results_dict
