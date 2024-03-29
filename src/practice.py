import os
from typing import Optional

from dir_utils import get_practices_dir
from plan import get_plan_dir


def create_practice(
    session_type: str,
    plan: str,
    activity: str,
    date: str,
    practice_name: Optional[str] = None,
    error_if_exists: bool = True,
):
    plan_dir = get_plan_dir(plan=plan, activity=activity)

    session_path = os.path.join(plan_dir, session_type + ".md")
    if not os.path.isfile(session_path):
        raise FileNotFoundError(session_path)

    practice_dir = get_practices_dir(activity=activity)
    if not os.path.isdir(practice_dir):
        os.mkdir(practice_dir)

    practice_year, practice_month, _ = date.split("-")
    year_dir = os.path.join(practice_dir, practice_year)
    if not os.path.isdir(year_dir):
        os.mkdir(year_dir)

    month_dir = os.path.join(
        practice_dir, practice_year, f"{practice_year}-{practice_month}"
    )
    if not os.path.isdir(month_dir):
        os.mkdir(month_dir)

    if practice_name is None:
        practice_name = " ".join([date, plan, "-", session_type])
    practice_filename = practice_name + ".md"

    practice_path = os.path.join(month_dir, practice_filename)
    if os.path.isfile(practice_path):
        if error_if_exists:
            raise FileExistsError(practice_path)
        else:
            # just skip creating the practice.
            return

    # extract exercises from session plan
    with open(session_path, "r") as file:
        lines = file.readlines()

    exercises = []
    current_exercise = {}
    for line in lines[1:]:
        # new exercise!
        if not line.startswith("\t"):
            # if valid, save current exercise
            current_exercise = {"Name": line[2:-1].strip()}
            if "Name" in current_exercise:
                exercises.append(current_exercise)
        else:
            key = line.split(":")[0][3:].strip()
            val = ":".join(line.split(":")[1:]).strip()
            current_exercise[key] = val

    with open(os.path.join(practice_dir, practice_path), "w") as file:
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
