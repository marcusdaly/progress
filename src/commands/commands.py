"""
Main functionality of the app.
"""
from config import create_config, get_activity_directory

import os


"""
Config
"""
def handle_config_command(activity_directory: str):
    create_config(activity_directory=activity_directory)

"""
Activity
"""
def handle_activity_create_command(name: str):
    # TODO check if exists
    activity_directory = get_activity_directory()
    os.mkdir(os.path.join(activity_directory, name))

def handle_activity_ls_command():
    activity_directory = get_activity_directory()
    paths = os.listdir(activity_directory)
    activities = [path for path in paths if os.path.isdir(os.path.join(activity_directory, path)) and not path.startswith(".")]
    print("Activities:\n\t" + "\n\t".join(activities))

def handle_activity_info_command(name: str):
    pass

"""
Skill
"""
def handle_skill_create_command(name: str):
    pass

def handle_skill_ls_command():
    pass

def handle_skill_info_command(name: str):
    pass

"""
Plan
"""
def handle_plan_create_command(name: str):
    pass

def handle_plan_ls_command():
    pass

def handle_plan_info_command(name: str):
    pass

"""
Practice
"""
def handle_practice_create_command(name: str):
    pass

def handle_practice_ls_command():
    pass

def handle_practice_info_command(name: str):
    pass