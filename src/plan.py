import datetime
import os
from typing import List, Optional

from activity import get_activity_dir


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


def create_plan(plan: str, activity: str):
    # add on date to activity name:
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    plan_dir = get_plan_dir(plan=plan, activity=activity, date=date)
    if os.path.isdir(plan_dir):
        raise ValueError(plan)
    os.mkdir(plan_dir)

    schedule_name = "Schedule.md"
    with open(os.path.join(plan_dir, schedule_name), "w") as file:
        file.write("# Monday\n")
        file.write("- SESSION TYPE\n")
        file.write("\t- (HH:MM - HH:MM)\n")
        file.write("# Tuesday\n")
        file.write("- SESSION TYPE\n")
        file.write("\t- (HH:MM - HH:MM)\n")
        file.write("# Wednesday\n")
        file.write("- SESSION TYPE\n")
        file.write("\t- (HH:MM - HH:MM)\n")
        file.write("# Thursday\n")
        file.write("- SESSION TYPE\n")
        file.write("\t- (HH:MM - HH:MM)\n")
        file.write("# Friday\n")
        file.write("- SESSION TYPE\n")
        file.write("\t- (HH:MM - HH:MM)\n")
        file.write("# Saturday\n")
        file.write("- SESSION TYPE\n")
        file.write("\t- (HH:MM - HH:MM)\n")
        file.write("# Sunday\n")
        file.write("- SESSION TYPE\n")
        file.write("\t- (HH:MM - HH:MM)\n")

    session_name = "SESSION TYPE.md"
    with open(os.path.join(plan_dir, session_name), "w") as file:
        file.write("# SESSION TYPE\n")
        file.write("- SAMPLE EXERCISE\n")
        file.write("\t- Metric: Completion | Seconds | Reps | Variation | Weight\n")
        file.write("\t- Reps: 5 - 10\n")
        file.write("\t- Time: 5 sec\n")
        file.write("\t- Rest: 2 mins\n")
        file.write("\t- Sets: 2\n")


def get_plans(activity: str) -> List[str]:
    activity_plan_dir = os.path.join(get_activity_dir(activity), "Plan")
    plan_paths = os.listdir(activity_plan_dir)
    plans = [
        path
        for path in plan_paths
        if os.path.isdir(os.path.join(activity_plan_dir, path))
        and not path.startswith(".")
    ]
    return plans


def get_plan(name: str):
    pass
