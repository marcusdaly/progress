# progress
`progress` is a tool to planning, tracking, and visualizing progress of all kinds. We'll try to make it as easy as possible but you have to put in the real effort.

# Overview
First, we'll go over what `progress` has to offer.
## Activities
In order to work its magic, `progress` interfaces with a directory on your computer that holds information on your progress for a specific **activity**. 

Example activities:
- Rock Climbing
- Calisthenics
- Park Skiing
- Typing

## Skills
Each activity may encompass a variety of **skills**. These skills are specific parts of an activity that should be in some way measurable.

Of course, it can be hard to categorize some skills into discrete categoires—maybe you're trying to land a front 270 out one week and a front swap the next. You might keep track of these each as their own skill, but we can view these as more overarching skills later, like "Frontside spins on rails" or even "Rail Tricks."

## Practice
In order to progress, you need to **practice**. `progress` can track your practices in a few main ways:
1. Track when you show up. This is a prerequisite for everything else, so you should know when you do this!
2. Track the content & success of your practices. Whether this is weight/sets/reps, words per minute, or whether you stomped the trick, we can track it. Don't want to get bogged down and distracted by tracking every little thing? No worries. Track as much detail as you like (e.g. "50% of my session I projected some V6-V7 slab problems, then I finished up with some easier overhangs & campusing")
3. Key qualitative notes from your practice. If you're trying to hold a handstand longer and you finally find something that ticked, you *need* to remember what you did. Track some notes, maybe even link a video showing what you did right.

## Planning
Planning is important in order to guide our progress toward our goals. There are two high-level parts of planning:
1. **Long-term schedule**. How many days a week are you climbing? How many sets a week are you training each muscle group? Get a plan together that you can follow.
2. **Individual session plan**. What exercises are you doing on your leg days? When during your typing practice will you add in punctuation to your all-lowercase typing? If you can have roughly do the same thing on the same days on a weekly basis, great. Try to abstract to some level where you can reliably repeat this schedule for many sessions, and you can go into the details in your practice log. Finally, this should also outline what information should be recorded about this session.

# Usage
Now that we know what `progress` had to offer, let's see how we can use it.

## Setup
0. Optionally, use [Obsidian](https://obsidian.md/) to visualize your files (this will be the easiest way to write plans, log your practices, etc.)
1. Create whatever activities you want to progress in.
2. List out some skills that fall under those activities. No worries if you miss some or realize later that some skill intersects multiple activities—we'll be able to adjust for that.
3. Write out your plan for how you're going to practice.
4. Follow that plan and log your practices.
5. See your progression and use that to inform your future plans!


---
# Development
If you just want to use `progress` but not contribute to it, no need to read further! 

If you for whatever reason do feel like contributing, we'll go over the dev setup and outline of the project here.

## Getting Started
First, pre-requisites:
- python3.9

Once you have python set up (preferably in a virtual environment), install the python requirements at `requirements.txt` with something like `python -m pip install -r requirements.txt`. 

For convenience, we have provided a `.pre-commit-config.yml` file. This will run all linting & formatting on your code before making a commit. Please run `pre-commit install` to set up pre-commit hooks before making commits to use this.

## Code Outline
Super simple now. Source code goes under `src`. This just contains a script, `main.py`.

## Managing Dependencies
We use `pip-compile` from [`pip-tools`](https://github.com/jazzband/pip-tools) to manage python dependencies. Add in whatever python packages and version requirements to `requirements.in`, then run `pip-compile` to automatically generate a `requirements.txt` file with specific versions of everything that match your specifications in `requirements.in`.

