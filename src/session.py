import os
from typing import List

from plan import get_plan_dir


def create_session(session_type: str, plan: str, activity: str):

    plan_dir = get_plan_dir(plan=plan, activity=activity)
    if not os.path.isdir(plan_dir):
        raise FileNotFoundError(plan_dir)

    session_name = f"{session_type}.md"
    session_path = os.path.join(plan_dir, session_name)
    if os.path.isfile(session_path):
        raise FileExistsError(session_path)

    with open(session_path, "w") as file:
        file.write(f"# {session_type}\n")
        file.write("- SAMPLE EXERCISE\n")
        file.write("\t- Metric: Completion | Seconds | Reps | Variation | Weight\n")
        file.write("\t- Reps: 5 - 10\n")
        file.write("\t- Time: 5 sec\n")
        file.write("\t- Rest: 2 mins\n")
        file.write("\t- Sets: 2\n")


def get_sessions(plan: str, activity: str) -> List[str]:
    plan_dir = get_plan_dir(plan=plan, activity=activity)
    if not os.path.isdir(plan_dir):
        raise FileNotFoundError(plan_dir)

    plan_paths = os.listdir(plan_dir)
    sessions = [
        path[:-3]
        for path in plan_paths
        if os.path.isfile(os.path.join(plan_dir, path))
        and not path.startswith(".")
        and path != "Schedule.md"
    ]
    return sessions
