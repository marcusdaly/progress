"""
Main functionality of the app.
"""
from activity import create_activity, get_activities, get_activity
from config import create_config
from plan import create_plan, get_plans, schedule
from practice import create_practice
from session import create_session, get_sessions
from skill import create_skill, get_skills

"""
Config
"""


def handle_config_command(activity_vault: str):
    create_config(activity_vault=activity_vault)


"""
Activity
"""


def handle_activity_create_command(activity: str):
    create_activity(activity)


def handle_activity_ls_command():
    activities = get_activities()
    print("Activities:\n\t" + "\n\t".join(activities))


def handle_activity_info_command(activity: str):
    activity = get_activity(activity=activity)
    print(activity)


"""
Skill
"""


def handle_skill_create_command(skill: str, activity: str):
    create_skill(skill=skill, activity=activity)


def handle_skill_ls_command(activity: str):
    skills = get_skills(activity=activity)
    print(f"{activity} Skills:\n\t" + "\n\t".join(skills))


def handle_skill_info_command(skill: str):
    pass


"""
Plan
"""


def handle_plan_create_command(plan: str, activity: str):
    create_plan(plan=plan, activity=activity)


def handle_plan_ls_command(activity: str):
    plans = get_plans(activity=activity)
    print(f"{activity} Plans:\n\t" + "\n\t".join(plans))


def handle_plan_info_command(plan: str):
    pass


def handle_plan_schedule_command(until: str, plan: str, activity: str):
    schedule(until=until, plan=plan, activity=activity)


"""
Session
"""


def handle_session_create_command(session_type: str, plan: str, activity: str):
    create_session(session_type=session_type, plan=plan, activity=activity)


def handle_session_ls_command(plan: str, activity: str):
    sessions = get_sessions(plan=plan, activity=activity)
    print(f"{activity} - {plan} Sessions:\n\t" + "\n\t".join(sessions))


def handle_session_info_command(practice: str, activity: str):
    pass


"""
Practice
"""


def handle_practice_create_command(
    session_type: str, plan: str, activity: str, date: str
):
    create_practice(session_type=session_type, plan=plan, activity=activity, date=date)


def handle_practice_ls_command(activity: str):
    pass


def handle_practice_info_command(practice: str, activity: str):
    pass
