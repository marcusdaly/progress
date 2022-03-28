import os
from typing import List

from config import get_activity_vault


def get_activity_dir(activity: str):
    activity_vault = get_activity_vault()
    activity_dir = os.path.join(activity_vault, activity)
    return activity_dir


def create_activity(name: str):
    activity_dir = get_activity_dir(name)
    # create the activity
    os.mkdir(activity_dir)

    # and create subdirectories under this activity
    os.mkdir(os.path.join(activity_dir, "Skill"))
    os.mkdir(os.path.join(activity_dir, "Plan"))
    os.mkdir(os.path.join(activity_dir, "Practice"))


def get_activities() -> List[str]:
    activity_vault = get_activity_vault()
    activity_paths = os.listdir(activity_vault)
    activities = [
        path
        for path in activity_paths
        if os.path.isdir(os.path.join(activity_vault, path))
        and not path.startswith(".")
    ]
    return activities


def get_activity(name: str):
    pass
