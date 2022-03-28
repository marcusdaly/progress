import os
from typing import List

from activity import get_activity_dir


def get_skill_dir(skill: str, activity: str) -> str:
    activity_dir = get_activity_dir(activity)
    skill_dir = os.path.join(activity_dir, "Skill", skill)
    return skill_dir


def create_skill(skill: str, activity: str):
    skill_dir = get_skill_dir(skill=skill, activity=activity)
    os.mkdir(skill_dir)


def get_skills(activity: str) -> List[str]:
    activity_skill_dir = os.path.join(get_activity_dir(activity), "Skill")
    skill_paths = os.listdir(activity_skill_dir)
    skills = [
        path
        for path in skill_paths
        if os.path.isdir(os.path.join(activity_skill_dir, path))
        and not path.startswith(".")
    ]
    return skills


def get_skill(name: str):
    pass
