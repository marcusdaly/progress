import os

from dir_utils import (
    get_report_dir,
    get_report_path,
    get_report_template_path,
    get_report_visualization_path,
    get_reports_dir,
    strip_before_activity,
)
from exercise import get_exercise, visualize_exercise_data


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
        for line in lines:
            if line.startswith("- Exercise:"):
                exercises.append(line.removeprefix("- Exercise:").strip())
            if line.startswith("- Start:"):
                start_date = line.removeprefix("- Start:").strip()

        if len(exercises) == 0:
            raise ValueError(exercises)

        all_data = {}
        for exercise in exercises:
            all_data = all_data | get_exercise(
                activity=activity, exercise=exercise, start=start_date
            )

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
