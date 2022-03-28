import os

from activity import get_activity_dir
from plan import get_plan_dir


def get_practice_dir(activity: str) -> str:
    activity_dir = get_activity_dir(activity)
    practice_dir = os.path.join(activity_dir, "Practice")
    return practice_dir


def create_practice(session_type: str, plan: str, activity: str, date: str):
    plan_dir = get_plan_dir(plan=plan, activity=activity)

    session_path = os.path.join(plan_dir, session_type + ".md")
    if not os.path.isfile(session_path):
        raise ValueError(session_path)

    practice_dir = get_practice_dir(activity=activity)
    if not os.path.isdir(practice_dir):
        os.mkdir(practice_dir)

    practice_name = " ".join([date, plan, "-", session_type]) + ".md"
    if os.path.isfile(os.path.join(practice_dir, practice_name)):
        raise ValueError(practice_name)

    # extract exercises from session plan
    with open(session_path, "r") as file:
        lines = file.readlines()

    exercises = []
    current_exercise = {}
    for line in lines[1:]:
        # new exerscise!
        if not line.startswith("\t"):
            # if valid, save current exercise
            if "Name" in current_exercise:
                exercises.append(current_exercise)

            current_exercise = {"Name": line[2:-1].strip()}
        else:
            key = line.split(":")[0][3:].strip()
            val = ":".join(line.split(":")[1:]).strip()
            current_exercise[key] = val

    with open(os.path.join(practice_dir, practice_name), "w") as file:
        file.write(f"# {session_type}\n")
        file.write("### HH:MM - HH:MM\n")

        # loop through exercises and put them here!
        for exercise in exercises:
            name = exercise["Name"]
            metric = exercise["Metric"]
            reps = exercise.get("Reps", None)
            time = exercise.get("Time", None)
            rest = exercise.get("Rest", None)
            sets = exercise.get("Sets", None)
            note = exercise.get("Note", None)

            is_completion = metric == "Completion"
            top_level_checkbox_str = " [ ] " if is_completion and sets is None else " "
            set_checkbox_str = " [ ] " if is_completion and sets is not None else " "

            file.write(f"-{top_level_checkbox_str}{name}\n")

            file.write(f"\t- Metric: {metric}\n")
            if reps is not None:
                file.write(f"\t- Reps: {reps}\n")
            if time is not None:
                file.write(f"\t- Time: {time}\n")
            if rest is not None:
                file.write(f"\t- Rest: {rest}\n")
            if sets is not None:
                file.write(f"\t- Sets: {sets}\n")
            if note is not None:
                file.write(f"\t- Note: {note}\n")

            # if not completion we'll still have to give
            # results for the single set
            if not is_completion and sets is None:
                sets = 1
            if sets is not None:
                for set_num in range(1, int(sets) + 1):
                    file.write(f"\t{set_num}.{set_checkbox_str}\n")

        file.write("\n## Notes\n")
        file.write("- ")
