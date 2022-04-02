import datetime
import os
from typing import List

from activity import get_activity_dir
from dir_utils import get_plan_dir
from practice import create_practice

DOW_TO_INT = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}


def create_plan(plan: str, activity: str):
    # add on date to activity name:
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    plan_dir = get_plan_dir(plan=plan, activity=activity, date=date)
    if os.path.isdir(plan_dir):
        raise ValueError(plan)
    os.mkdir(plan_dir)

    schedule_name = "Schedule.md"
    schedule_path = os.path.join(plan_dir, schedule_name)
    if os.path.isfile(schedule_path):
        raise ValueError(schedule_path)

    with open(schedule_path, "w") as file:
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


def schedule(until: str, plan: str, activity: str):
    until_date = datetime.datetime.strptime(until, "%Y-%m-%d")
    date = datetime.datetime.now()

    plan_dir = get_plan_dir(plan=plan, activity=activity)
    if not os.path.isdir(plan_dir):
        raise ValueError(plan)
    schedule_name = "Schedule.md"
    schedule_path = os.path.join(plan_dir, schedule_name)
    if not os.path.isfile(schedule_path):
        raise ValueError(schedule_path)

    with open(schedule_path, "r") as file:
        lines = file.readlines()

    dow_sessions = [[] for _ in range(7)]
    current_dow_sessions = []
    dow_index = None
    for line in lines:
        if line.startswith("# "):
            # new DoW, so done with last DoW
            if len(current_dow_sessions) > 0:
                dow_sessions[dow_index] = current_dow_sessions
                current_dow_sessions = []

            dow = line[2:-1].strip()
            dow_index = DOW_TO_INT[dow]
        elif line.startswith("- "):
            session_type = line[2:-1]
            if session_type != "Rest":
                current_dow_sessions.append({"Session Type": session_type})
        elif line.startswith("\t- "):
            times = line[3:-1]
            current_dow_sessions[-1]["Times"] = times

    # for last day, still may need to add the sessions.
    if len(current_dow_sessions) > 0:
        dow_sessions[dow_index] = current_dow_sessions

    while until_date > date:
        date_str = date.strftime("%Y-%m-%d")
        dow_index = date.weekday()

        # create practices for all sessions on this DoW
        # if multiple of same name, enumerate with numbers

        sessions = dow_sessions[dow_index]

        # before creating any, plan out their names.
        session_names = [
            " ".join([date_str, plan, "-", session["Session Type"]])
            for session in sessions
        ]

        # if need to enumerate, do so
        if list(set(session_names)) != session_names:
            # for each session that has multiple, append a number
            session_counts = {}
            for session_name in session_names:
                if session_name in session_counts:
                    session_counts[session_name] += 1
                else:
                    session_counts[session_name] = 1

            sessions_seen = {session_name: 0 for session_name in session_names}
            for session_idx, session_name in enumerate(session_names):
                if session_counts[session_name] > 1:
                    sessions_seen[session_name] += 1
                    session_names[
                        session_idx
                    ] = f"{session_name} {sessions_seen[session_name]}"

        # create the practices from the sessions
        for session, session_name in zip(sessions, session_names):
            create_practice(
                session_type=session["Session Type"],
                plan=plan,
                activity=activity,
                date=date_str,
                practice_name=session_name,
                error_if_exists=False,
            )

        date = date + datetime.timedelta(days=1)


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
