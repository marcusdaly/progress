import os
from typing import Optional

from config import get_activity_vault


def get_activity_dir(activity: str) -> str:
    activity_vault = get_activity_vault()
    activity_dir = os.path.join(activity_vault, activity)
    return activity_dir


def get_reports_dir(activity: str) -> str:
    reports_dir = os.path.join(get_activity_dir(activity), "Report")
    if not os.path.isdir(reports_dir):
        os.mkdir(reports_dir)

    return reports_dir


def get_report_dir(name: str, activity: str) -> str:
    reports_dir = get_reports_dir(activity)
    report_dir = os.path.join(reports_dir, name)
    return report_dir


def get_report_path(name: str, activity: str) -> str:
    report_dir = get_report_dir(name, activity)
    report_template_path = os.path.join(report_dir, "Report.md")
    return report_template_path


def get_report_visualization_path(name: str, activity: str) -> str:
    report_dir = get_report_dir(name, activity)
    report_template_path = os.path.join(report_dir, "Visualization.png")
    return report_template_path


def get_report_template_path(name: str, activity: str) -> str:
    report_dir = get_report_dir(name, activity)
    report_template_path = os.path.join(report_dir, "Template.md")
    return report_template_path


def get_plan_dir(plan: str, activity: str, date: Optional[str] = None) -> str:
    activity_dir = get_activity_dir(activity)
    plans_dir = os.path.join(activity_dir, "Plan")
    if date is None:
        # find date corresponding to this plan
        matches = [
            path
            for path in os.listdir(plans_dir)
            if os.path.isdir(os.path.join(plans_dir, path)) and path.endswith(plan)
        ]
        if len(matches) > 1:
            raise ValueError(matches)
        if len(matches) == 0:
            raise ValueError(plan)
        date = matches[0].split(" ")[0]
    plan = " ".join([date, plan])
    plan_dir = os.path.join(plans_dir, plan)
    return plan_dir


def get_practices_dir(activity: str) -> str:
    activity_dir = get_activity_dir(activity)
    practices_dir = os.path.join(activity_dir, "Practice")
    return practices_dir


def strip_before_activity(path: str, activity: str) -> str:
    """
    Strip all parts of the path that come before the activity.
    """
    split_path = path.split("/")
    split_activity_path = split_path[split_path.index(activity) :]
    activity_path = "/".join(split_activity_path)
    return activity_path
