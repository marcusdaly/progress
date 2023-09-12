import os

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


def generate_reports(activity: str):
    reports_dir = get_reports_dir(activity)
    for report_name in os.listdir(reports_dir):
        report_template_path = get_report_template_path(report_name, activity)
        with open(report_template_path, "r") as file:
            lines = file.readlines()

        exercises = []
        start_date = None
        bodyweight = None
        for line in lines:
            if line.startswith("- Exercise:"):
                exercises.append(line.removeprefix("- Exercise:").strip())
            if line.startswith("- Start:"):
                start_date = line.removeprefix("- Start:").strip()
            if line.startswith("- Bodyweight:"):
                bodyweight = line.removeprefix("- Bodyweight:").strip()

        # TODO actually parameterize in report for "Weight" exercises.
        weight_exercises = [
            exercise for exercise in exercises if "(Weight)" in exercise
        ]
        weight_exercise_params = {
            exercise: {
                "is_bw_exercise": True,
                "normalize_by_bw": True,
                "calculate_orm": True,
            }
            for exercise in weight_exercises
        }

        if len(exercises) == 0:
            raise ValueError(exercises)

        all_data = {}
        # TODO probably keep all info for a single exercise in a single df.
        # reps, weight, all of it.
        for exercise in exercises:
            all_data = all_data | get_exercise(
                activity=activity, exercise=exercise, start=start_date
            )

        if bodyweight is not None:
            bodyweight_data = get_exercise(
                activity="Fitness", exercise=bodyweight, start=start_date
            )

            print(bodyweight_data)
            bodyweight_data = bodyweight_data[f"{bodyweight} (Weight)"]
            print(bodyweight_data)
            del bodyweight_data["Session"]
            del bodyweight_data["Set"]

            for exercise, data in all_data.items():
                if "(Weight)" in exercise:
                    bw_col = f"{bodyweight} (Weight)"
                    merged = pd.merge(data, bodyweight_data, how="outer", on="Date")
                    base_exercise = exercise.removesuffix(" (Weight)")
                    reps_exercise = f"{base_exercise} (Reps)"
                    merged = pd.merge(
                        all_data[reps_exercise], merged, how="outer", on=["Date", "Set"]
                    )
                    merged[bw_col] = merged[bw_col].ffill().bfill()
                    merged = merged.dropna(subset=[exercise, reps_exercise])

                    # calculate ORM
                    if weight_exercise_params["calculate_orm"]:
                        # TODO vectorize calculate ORM
                        merged[exercise] = [
                            calculate_orm(
                                row[exercise],
                                row[reps_exercise],
                                bodyweight=row[bw_col],
                            )
                            for _, row in merged.iterrows()
                        ]
                        # TODO figure out difference in lengths here.
                        print(merged[exercise])
                        print(data[exercise])
                        data[exercise] = merged[exercise]

                    # normalize by bodyweight
                    if weight_exercise_params["normalize_by_bw"]:
                        data[exercise] = data[exercise] / merged[bw_col]
        else:
            # TODO calculate ORM if specified
            pass

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
