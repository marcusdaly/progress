"""
Functions to parse out arguments and call appropriate functions.
"""
from argparse import Namespace

from commands.commands import (
    handle_activity_create_command,
    handle_activity_info_command,
    handle_activity_ls_command,
    handle_config_command,
    handle_exercise_compare_command,
    handle_exercise_info_command,
    handle_exercise_ls_command,
    handle_plan_create_command,
    handle_plan_info_command,
    handle_plan_ls_command,
    handle_plan_schedule_command,
    handle_plan_visualize_command,
    handle_practice_create_command,
    handle_practice_info_command,
    handle_practice_ls_command,
    handle_report_generate_command,
    handle_report_template_command,
    handle_session_create_command,
    handle_session_info_command,
    handle_session_ls_command,
    handle_skill_create_command,
    handle_skill_info_command,
    handle_skill_ls_command,
)

"""
Config Commands
"""


def handle_config_cli_command(args: Namespace):
    handle_config_command(activity_vault=args.directory)


"""
Activity Commands
"""


def handle_activity_cli_command(args: Namespace):
    subcommands = {
        "create": _handle_activity_create_cli_command,
        "ls": _handle_activity_ls_cli_command,
        "info": _handle_activity_info_cli_command,
    }

    subcommands[args.subcommand](args)


def _handle_activity_create_cli_command(args: Namespace):
    handle_activity_create_command(activity=args.name)


def _handle_activity_ls_cli_command(args: Namespace):
    handle_activity_ls_command()


def _handle_activity_info_cli_command(args: Namespace):
    handle_activity_info_command(activity=args.name)


"""
Report Commands
"""


def handle_report_cli_command(args: Namespace):
    subcommands = {
        "template": _handle_report_template_cli_command,
        "generate": _handle_report_generate_cli_command,
    }

    subcommands[args.subcommand](args)


def _handle_report_template_cli_command(args: Namespace):
    handle_report_template_command(name=args.name, activity=args.activity)


def _handle_report_generate_cli_command(args: Namespace):
    handle_report_generate_command(activity=args.activity)


"""
Skill Commands
"""


def handle_skill_cli_command(args: Namespace):
    subcommands = {
        "create": _handle_skill_create_cli_command,
        "ls": _handle_skill_ls_cli_command,
        "info": _handle_skill_info_cli_command,
    }

    subcommands[args.subcommand](args)


def _handle_skill_create_cli_command(args: Namespace):
    handle_skill_create_command(skill=args.name, activity=args.activity)


def _handle_skill_ls_cli_command(args: Namespace):
    handle_skill_ls_command(activity=args.activity)


def _handle_skill_info_cli_command(args: Namespace):
    handle_skill_info_command(skill=args.name)


"""
Plan Commands
"""


def handle_plan_cli_command(args: Namespace):
    subcommands = {
        "create": _handle_plan_create_cli_command,
        "ls": _handle_plan_ls_cli_command,
        "info": _handle_plan_info_cli_command,
        "schedule": _handle_plan_schedule_cli_command,
        "visualize": _handle_plan_visualize_command,
    }

    subcommands[args.subcommand](args)


def _handle_plan_create_cli_command(args: Namespace):
    handle_plan_create_command(plan=args.name, activity=args.activity)


def _handle_plan_ls_cli_command(args: Namespace):
    handle_plan_ls_command(activity=args.activity)


def _handle_plan_info_cli_command(args: Namespace):
    handle_plan_info_command(plan=args.name)


def _handle_plan_schedule_cli_command(args: Namespace):
    handle_plan_schedule_command(
        until=args.until, plan=args.name, activity=args.activity
    )


def _handle_plan_visualize_command(args: Namespace):
    handle_plan_visualize_command(plan=args.plan, activity=args.activity)


"""
Session Commands
"""


def handle_session_cli_command(args: Namespace):
    subcommands = {
        "create": _handle_session_create_cli_command,
        "ls": _handle_session_ls_cli_command,
        "info": _handle_session_info_cli_command,
    }

    subcommands[args.subcommand](args)


def _handle_session_create_cli_command(args: Namespace):
    handle_session_create_command(
        session_type=args.name, plan=args.plan, activity=args.activity
    )


def _handle_session_ls_cli_command(args: Namespace):
    handle_session_ls_command(plan=args.plan, activity=args.activity)


def _handle_session_info_cli_command(args: Namespace):
    handle_session_info_command(session=args.name)


"""
Practice Commands
"""


def handle_practice_cli_command(args: Namespace):
    subcommands = {
        "create": _handle_practice_create_cli_command,
        "ls": _handle_practice_ls_cli_command,
        "info": _handle_practice_info_cli_command,
    }

    subcommands[args.subcommand](args)


def _handle_practice_create_cli_command(args: Namespace):
    handle_practice_create_command(
        session_type=args.session,
        plan=args.plan,
        activity=args.activity,
        date=args.date,
    )


def _handle_practice_ls_cli_command(args: Namespace):
    handle_practice_ls_command(activity=args.activity)


def _handle_practice_info_cli_command(args: Namespace):
    handle_practice_info_command(practice=args.name)


"""
Exercise Commands
"""


def handle_exercise_cli_command(args: Namespace):
    subcommands = {
        "ls": _handle_exercise_ls_cli_command,
        "info": _handle_exercise_info_cli_command,
        "compare": _handle_exercise_compare_cli_command,
    }

    subcommands[args.subcommand](args)


def _handle_exercise_ls_cli_command(args: Namespace):
    handle_exercise_ls_command(activity=args.activity)


def _handle_exercise_info_cli_command(args: Namespace):
    handle_exercise_info_command(
        activity=args.activity, exercise=args.name, start=args.start
    )


def _handle_exercise_compare_cli_command(args: Namespace):
    handle_exercise_compare_command(
        activity_1=args.activity1,
        exercise_1=args.name1,
        activity_2=args.activity2,
        exercise_2=args.name2,
        start=args.start,
    )
