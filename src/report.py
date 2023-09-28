import os
from typing import List

import pandas as pd

from dir_utils import (
    get_report_dir,
    get_report_path,
    get_report_template_path,
    get_report_visualization_path,
    get_reports_dir,
    strip_before_activity,
)
from exercise import get_exercise, visualize_exercise_data
from orm_calculations import calculate_orm


def create_report_template(name: str, activity: str):
    report_dir = get_report_dir(name, activity)
    if os.path.isdir(report_dir):
        raise FileExistsError(report_dir)
    os.mkdir(report_dir)

    report_template_path = get_report_template_path(name, activity)
    if os.path.isfile(report_template_path):
        raise FileExistsError(report_template_path)

    with open(report_template_path, "w") as file:
        file.write("- Exercise: exercise name 1 here")
        file.write("\n- Exercise: exercise name 2 here (optional, can put more)")
        file.write("\n- Start: YYYY-MM-DD (optional)")


def _get_metrics_for_exercise_data(exercise_data: pd.DataFrame) -> List[str]:
    return [
        col for col in exercise_data.columns if col not in {"Set", "Date", "Session"}
    ]


def generate_reports(activity: str):
    reports_dir = get_reports_dir(activity)
    for report_name in os.listdir(reports_dir):
        report_template_path = get_report_template_path(report_name, activity)
        with open(report_template_path, "r") as file:
            lines = file.readlines()

        exercises = []
        start_date = None

        weight_cols = ["Weight", "Weight Left", "Weight Right"]
        weight_to_reps_col = {
            "Weight": "Reps",
            "Weight Left": "Reps Left",
            "Weight Right": "Reps Right",
        }

        # This is a hard-coded exercise name representing your "bodyweight" measurement.
        bodyweight = "Weight"
        is_bodyweight_exercise = False
        normalize_by_bodyweight = False
        for line in lines:
            if line.startswith("- Exercise:"):
                exercises.append(line.removeprefix("- Exercise:").strip())
            if line.startswith("- Start:"):
                start_date = line.removeprefix("- Start:").strip()
            if line.startswith("- Is Bodyweight Exercise"):
                is_bodyweight_exercise = True
            if line.startswith("- Normalize by Bodyweight"):
                normalize_by_bodyweight = True

        if len(exercises) == 0:
            raise ValueError(exercises)

        all_data = {
            exercise: get_exercise(
                activity=activity, exercise=exercise, start=start_date
            )
            for exercise in exercises
        }

        # TODO actually parameterize in report for "Weight" exercises.
        weight_exercises = [
            exercise
            for exercise, data in all_data.items()
            if any(col in data.columns for col in weight_cols)
        ]
        weight_exercise_params = {
            exercise: {
                "is_bw_exercise": is_bodyweight_exercise,
                "normalize_by_bw": normalize_by_bodyweight,
                "calculate_orm": True,
                "set_agg_func": "max",
                # "set_agg_func": None,
            }
            for exercise in weight_exercises
        }

        if bodyweight is not None:
            bodyweight_data = get_exercise(
                activity="Fitness", exercise=bodyweight, start=start_date
            )
            bodyweight_data["Bodyweight"] = bodyweight_data["Weight"]
            del bodyweight_data["Weight"]

        for exercise, data in all_data.items():
            data["data_index"] = data.index.to_numpy()
            for weight_col in [col for col in data.columns if col in weight_cols]:
                col_of_interest = weight_col
                reps_col = weight_to_reps_col[weight_col]

                if bodyweight is not None:
                    bw_col = "Bodyweight"
                    # use temporary data index column to retain correct rows.
                    merged = pd.merge(data, bodyweight_data, how="outer", on="Date")
                    merged[bw_col] = merged[bw_col].ffill().bfill()
                    merged = merged.dropna(subset=["data_index"])
                    merged = merged.set_index("data_index")
                else:
                    merged = data.copy()

                # calculate ORM
                if (
                    reps_col in data.columns
                    and weight_exercise_params[exercise]["calculate_orm"]
                ):
                    if weight_exercise_params[exercise]["is_bw_exercise"]:
                        # TODO vectorize calculate ORM
                        merged[f"{col_of_interest} | ORM"] = [
                            calculate_orm(
                                row[col_of_interest],
                                row[reps_col],
                                bodyweight=row[bw_col],
                            )
                            for _, row in merged.iterrows()
                        ]
                    else:
                        # TODO vectorize calculate ORM
                        merged[f"{col_of_interest} | ORM"] = [
                            calculate_orm(
                                row[col_of_interest],
                                row[reps_col],
                            )
                            for _, row in merged.iterrows()
                        ]
                    col_of_interest = f"{col_of_interest} | ORM"
                    data.loc[merged.index, col_of_interest] = merged[col_of_interest]

                # normalize by bodyweight
                if weight_exercise_params[exercise]["normalize_by_bw"]:
                    merged[f"{col_of_interest} | %BW"] = (
                        merged[col_of_interest] / merged[bw_col] * 100
                    )
                    col_of_interest = f"{col_of_interest} | %BW"
                    data.loc[merged.index, col_of_interest] = merged[col_of_interest]
            del data["data_index"]

        # after doing any feature engineering, aggregate across sets.
        for exercise in weight_exercises:
            all_data[exercise] = (
                all_data[exercise]
                .groupby(["Date", "Session"], as_index=False)
                .agg(weight_exercise_params[exercise]["set_agg_func"])
            )
            del all_data[exercise]["Set"]

        # finally, start generating the results
        visualization_path = get_report_visualization_path(report_name, activity)
        results_dict = visualize_exercise_data(all_data, filename=visualization_path)

        lines = []
        for metric, metric_results in results_dict.items():
            lines.append(f"# {metric}")
            for metric_category, metric_category_stats in metric_results.items():
                lines.append(f"## {metric_category}")
                for stat, val in metric_category_stats.items():
                    lines.append(f"- {stat}: **{val:0.2f}**")

        lines.append("# Visualization")
        lines.append(f"![[{strip_before_activity(visualization_path, activity)}]]")
        report_results = "\n".join(lines)

        report_path = get_report_path(report_name, activity)
        with open(report_path, "w") as file:
            file.write(report_results)
