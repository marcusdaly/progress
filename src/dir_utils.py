import os
from typing import Optional

from config import get_activity_vault


def get_activity_dir(activity: str):
    activity_vault = get_activity_vault()
    activity_dir = os.path.join(activity_vault, activity)
    return activity_dir


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
