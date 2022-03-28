"""
Main entrypoint for progress app.
"""

import argparse
import logging

from commands.cli_commands import (
    handle_activity_cli_command,
    handle_config_cli_command,
    handle_plan_cli_command,
    handle_practice_cli_command,
    handle_skill_cli_command,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", help="increase output verbosity", action="store_true"
    )

    # high level commands
    subparsers = parser.add_subparsers(title="commands", dest="command", required=True)
    parser_config = subparsers.add_parser("config", help="sets a new configuration")
    parser_activity = subparsers.add_parser("activity", help="manage activities")
    parser_skill = subparsers.add_parser("skill", help="manage skills")
    parser_plan = subparsers.add_parser("plan", help="manage plans")
    parser_practice = subparsers.add_parser("practice", help="manage practices")

    # config
    parser_config.add_argument(
        "--directory", required=True, help="the directory of the activities vault"
    )

    # activity
    subparsers_activity = parser_activity.add_subparsers(
        title="subcommands", dest="subcommand", required=True
    )
    parser_activity_create = subparsers_activity.add_parser(
        "create", help="create a new activity"
    )
    parser_activity_ls = subparsers_activity.add_parser(
        "ls", help="list all activities"
    )
    parser_activity_info = subparsers_activity.add_parser(
        "info", help="get more info on a specific activity"
    )

    # activity create
    parser_activity_create.add_argument(
        "--name", required=True, help="the name of the new activity"
    )

    # activity ls
    # -- no arguments --

    # activity info
    parser_activity_info.add_argument(
        "--name", required=True, help="the name of the activity to get info on"
    )

    # skill
    subparsers_skill = parser_skill.add_subparsers(
        title="subcommands", dest="subcommand", required=True
    )
    parser_skill_create = subparsers_skill.add_parser(
        "create", help="create a new skill"
    )
    parser_skill_ls = subparsers_skill.add_parser("ls", help="list all activities")
    parser_skill_info = subparsers_skill.add_parser(
        "info", help="get more info on a specific skill"
    )

    # skill create
    parser_skill_create.add_argument(
        "--name", required=True, help="the name of the new skill"
    )
    parser_skill_create.add_argument(
        "--activity", required=True, help="the activity this skill is associated with"
    )

    # skill ls
    parser_skill_ls.add_argument(
        "--activity", required=True, help="the activity this skill is associated with"
    )

    # skill info
    parser_skill_info.add_argument(
        "--name", required=True, help="the name of the skill to get info on"
    )

    # plan
    subparsers_plan = parser_plan.add_subparsers(
        title="subcommands", dest="subcommand", required=True
    )
    parser_plan_create = subparsers_plan.add_parser("create", help="create a new plan")
    parser_plan_ls = subparsers_plan.add_parser("ls", help="list all activities")
    parser_plan_info = subparsers_plan.add_parser(
        "info", help="get more info on a specific plan"
    )

    # plan create
    parser_plan_create.add_argument(
        "--name", required=True, help="the name of the new plan"
    )
    parser_plan_create.add_argument(
        "--activity", required=True, help="the activity this plan is associated with"
    )

    # plan ls
    parser_plan_ls.add_argument(
        "--activity", required=True, help="the activity this plan is associated with"
    )

    # plan info
    parser_plan_info.add_argument(
        "--name", required=True, help="the name of the plan to get info on"
    )

    # practice
    subparsers_practice = parser_practice.add_subparsers(
        title="subcommands", dest="subcommand", required=True
    )
    parser_practice_create = subparsers_practice.add_parser(
        "create", help="create a new practice"
    )
    parser_practice_ls = subparsers_practice.add_parser("ls", help="list all practices")
    parser_practice_info = subparsers_practice.add_parser(
        "info", help="get more info on a specific practice"
    )

    # practice create
    parser_practice_create.add_argument(
        "--session", required=True, help="the session type of this practice"
    )
    parser_practice_create.add_argument(
        "--plan", required=True, help="the plan this practice originates from"
    )
    parser_practice_create.add_argument(
        "--activity", required=True, help="the activity being practiced"
    )
    parser_practice_create.add_argument(
        "--date", required=True, help="the date this practice is performed"
    )

    # practice ls
    # -- no arguments --

    # practice info
    parser_practice_info.add_argument(
        "--name", required=True, help="the name of the practice to get info on"
    )

    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.getLogger().setLevel(level)

    simple_args_commands = {
        "config": handle_config_cli_command,
        "activity": handle_activity_cli_command,
        "skill": handle_skill_cli_command,
        "plan": handle_plan_cli_command,
        "practice": handle_practice_cli_command,
    }

    if args.command in simple_args_commands:
        simple_args_commands[args.command](args)
