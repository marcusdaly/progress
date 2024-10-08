"""
Functionality to generate a logbook from climbing practices.
"""

import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from dir_utils import get_logbook_dir, get_practices_dir

plt.style.use("seaborn")


@dataclass(frozen=True)
class ClimbingEntry:
    name: str
    grade: str
    outcome: str
    description: Optional[str] = None


def parse_climbing_entry_grade_first_section(
    comma_split_entry: list[str],
) -> tuple[str, str]:
    grade_and_name = comma_split_entry[0]

    grade_split = grade_and_name.split(" V")
    if len(grade_split) < 2:
        raise ValueError(comma_split_entry)
    pre_grade = grade_split[0]
    post_v = grade_split[1]
    if len(post_v.split(" ")) > 0:
        grade_end = post_v.split(" ")[0]
    else:
        grade_end = post_v
    grade = "V" + grade_end
    post_grade = grade_and_name.removeprefix(f"{pre_grade} {grade}")

    name = pre_grade + post_grade

    print("grade", grade)
    print("name", name)
    return name, grade


def parse_climbing_entry_grade_second_section(
    comma_split_entry: list[str],
) -> ClimbingEntry:
    if len(comma_split_entry) < 3:
        raise ValueError(comma_split_entry)

    name, grade = comma_split_entry[0], comma_split_entry[1]

    # rest = comma_split_entry[2]

    # description = comma_split_entry.

    return ClimbingEntry(
        name=name,
        grade=grade,
        outcome="",
    )


def parse_climbing_entry(entry: str) -> ClimbingEntry:
    comma_split_entry = [section.strip() for section in entry.split(",")]

    if len(comma_split_entry) < 2:
        raise ValueError(entry)

    # handle case where grade in first section
    name, grade = parse_climbing_entry_grade_first_section(comma_split_entry)

    entry = ClimbingEntry(
        name=name,
        grade=grade,
        outcome="Unknown",
    )

    return entry


def _get_climbing_results_from_file(session_dir: str) -> Tuple[datetime, Dict]:
    found_exercise = False
    session_date_str = os.path.split(session_dir)[-1][:10]

    climbing_entries: Tuple[str, ClimbingEntry] = []

    # session_date = datetime.strptime(session_date_str, "%Y-%m-%d")
    exercise_results = {}
    with open(session_dir, "r") as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith("## Notes"):
            break
        if line.startswith("# "):
            skipped = "skipped" in line.lower()
            exercise_results["skipped"] = skipped
            if skipped:
                break
        elif line.startswith("- ") and ("Bouldering" in line or "Climbing" in line):
            found_exercise = True

        # elif line.startswith("\t- "):
        #     parse_climbing_entry(line)

        elif (
            found_exercise
            and line.startswith("\t")
            and len(line) >= 3
            and line[2] == "."
        ):
            try:
                climbing_entries.append(
                    (
                        session_date_str,
                        parse_climbing_entry(". ".join(line.split(". ")[1:])),
                    )
                )
            except ValueError:
                pass

    return climbing_entries


def get_climbing_data(activity: str, start: Optional[str] = None):
    if start is not None:
        start = datetime.strptime(start, "%Y-%m-%d")
    practices_dir = get_practices_dir(activity=activity)
    if not os.path.isdir(practices_dir):
        raise FileNotFoundError(practices_dir)

    all_entries = []
    for session_path, _, files in tqdm(os.walk(practices_dir)):
        for session in files:
            session_dir = os.path.join(session_path, session)
            # extract exercises from session plan
            entries = _get_climbing_results_from_file(session_dir)
            all_entries.extend(entries)

    return all_entries


def generate_logbook(activity: str):
    # logbook_dir = get_logbook_dir(activity)

    bouldering_data = get_climbing_data(activity=activity, start=None)
    plot_attempts(bouldering_data)


def plot_attempts(bouldering_data: list[tuple[str, ClimbingEntry]]):
    plt.figure(figsize=(20, 10))

    dates, entries = list(zip(*bouldering_data))

    grades = [entry.grade for entry in entries]
    grade_numbers = []
    for grade in grades:
        numbers = re.findall(r"\d+", grade)
        if len(numbers) == 0:
            grade_numbers.append(np.nan)
            continue
        number = numbers[0]

        grade_split = grade.split(number)

        if len(grade_split) > 1 and len(grade_split[1]) > 0:
            modifier = grade_split[1][0]
            if modifier == "+":
                modifier = 1 / 3
            elif modifier == "-":
                modifier = -1 / 3
            else:
                print("unknown modifier", modifier)
                modifier = 0
        else:
            modifier = 0

        number = float(number)
        if number >= 100:
            number /= 100

        number += modifier

        grade_numbers.append(number)
    print(dates, grade_numbers)
    plt.scatter(dates, grade_numbers, alpha=0.3)
    plt.xlabel("Date")
    plt.ylabel("V-grade")
    plt.show()
