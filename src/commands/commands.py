"""
Main functionality of the app.
"""
from activity import create_activity, get_activities, get_activity
from config import create_config
from exercise import get_exercise, get_exercises, visualize_exercise_data
from plan import create_plan, get_plans, schedule, visualize_plan
from practice import create_practice
from report import create_report_template, generate_reports
from session import create_session, get_sessions

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
Report
"""


def handle_report_template_command(name: str, activity: str):
    create_report_template(name, activity)


def handle_report_generate_command(activity: str):
    generate_reports(activity)


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


def handle_plan_visualize_command(plan: str, activity: str):
    visualize_plan(plan, activity)


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


"""
Exercise
"""


def handle_exercise_ls_command(activity: str):
    exercises = get_exercises(activity=activity)
    print(f"{activity} Exercises:\n\t" + "\n\t".join(exercises))


def handle_exercise_info_command(exercise: str, activity: str, start: str):
    all_data = get_exercise(activity=activity, exercise=exercise, start=start)
    visualize_exercise_data(all_data)


def handle_exercise_compare_command(
    exercise_1: str, activity_1: str, exercise_2: str, activity_2: str, start: str
):
    exercise_1_data = get_exercise(
        activity=activity_1, exercise=exercise_1, start=start
    )
    exercise_2_data = get_exercise(
        activity=activity_2, exercise=exercise_2, start=start
    )
    visualize_exercise_data(exercise_1_data | exercise_2_data)
