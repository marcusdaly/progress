"""
Functions to parse out arguments and call appropriate functions.
"""
from argparse import Namespace

from commands.commands import (
    handle_activity_create_command,
    handle_activity_info_command,
    handle_activity_ls_command,
    handle_config_command,
    handle_plan_create_command,
    handle_plan_info_command,
    handle_plan_ls_command,
    handle_practice_create_command,
    handle_practice_info_command,
    handle_practice_ls_command,
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
    }

    subcommands[args.subcommand](args)


def _handle_plan_create_cli_command(args: Namespace):
    handle_plan_create_command(plan=args.name, activity=args.activity)


def _handle_plan_ls_cli_command(args: Namespace):
    handle_plan_ls_command(activity=args.activity)


def _handle_plan_info_cli_command(args: Namespace):
    handle_plan_info_command(plan=args.name)


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
