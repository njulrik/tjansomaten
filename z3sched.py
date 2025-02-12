#!/usr/bin/env python3

from z3 import *

from model import *
from functools import reduce

import random

from functools import cmp_to_key

from typing import Tuple

import re

def varname(name, timeslot: Timeslot):
    return f"{timeslot}{SEPERATOR}{name}"

def get_var(name, timeslot: Timeslot):
    return Bool(varname(name, timeslot))

varname_pat = re.compile(r'(\w+) (\w+)\$(.+)')
def split_varname(var: str) -> Tuple[str, str, str]:
    m = varname_pat.match(var)
    if m is None:
        return None
    return m.group(1), m.group(2), m.group(3)


# SMT formula is structured as follows:
# Each timeslot needs to be filled, and each person should be available and have an approximately equal number of tasks.
# Variables are named <person>$<timeslot>, and have values in {0,1}.
# timeslot_goal: For each timeslot, the number of persons for the timeslot is equal to capacity.
# capacity_goal: for each person, number of timeslots is equally distributed.
# availability_goal: for each unavailable timeslot (person not present), add person$timeslot = 0.
# Solver goal is timeslot_goal AND capacity_goal AND availability_goal.
def schedule(names: List[str],
             weekend_list: List[str],
             calendar: List[Weekday],
             constraints: List[Constraint] = [],
             **kwargs
             ):
    random_level = kwargs.get('random', 1)
    if random_level >= 1:
        random.shuffle(names)
    big_task_needed = sum(
        map(lambda day: day.middag.needed + day.aften.needed, calendar)
    )
    small_task_needed = sum(map(lambda day: day.kaffe.needed, calendar))
    total_task_needed = big_task_needed + small_task_needed

    cap_upper = int(math.ceil(big_task_needed / len(names)))
    cap_lower = cap_upper - 1  # TODO work out that this always works

    timeslots = reduce(lambda acc, day: acc + day.needed(), calendar, [])
    if timeslots == []:
        raise ArgumentError("no needed timeslots in calendar")

    def single_ts_goal(names: List[str], timeslot: Timeslot):
        assert timeslot.needed != 0
        vars = [get_var(name, timeslot) for name in names]
        if random_level >= 1:
            random.shuffle(vars)
        return Sum(vars) == timeslot.needed
    
    def timeslots_goal(names, timeslots):
        return And([single_ts_goal(names, timeslot) for timeslot in timeslots])

    def single_cap_goal(name):
        sum = Sum([get_var(name, timeslot) for timeslot in timeslots])
        return And(sum <= cap_upper, sum >= cap_lower)

    def cap_goal():
        return And([single_cap_goal(name) for name in names])

    weekend_times = [ts for ts in timeslots if ts.name.lower().startswith('søndag') or ts.name.lower().startswith('lørdag')]
    weekend_constraint = And([Sum(get_var(name, timeslot)) == 0 for timeslot in weekend_times for name in names if name not in weekend_list])

    # solver goal: _all_ constraint `add`ed must be satisfied.
    s = Solver()
    s.add(weekend_constraint)
    s.add(cap_goal())
    s.add(timeslots_goal(names, timeslots))

    for cons in constraints:
        s.add(Sum(get_var(cons.name, cons.timeslot)) == (1 if cons.avail else 0))

    if s.check() == sat:
        m = s.model()
        sched = {}
        for var in m:
            if is_true(m[var]):
                day, time, name = split_varname(var.name())
                sched.setdefault((day, time), []).append(name)

        for (day, time), namelist in sorted(sched.items(), key=cmp_to_key(timeslot_order)):
            print(f"{day.capitalize():7} {time:10}\t{', '.join(sorted(namelist))}")

        for name in sorted(names):
            ntasks = len([l for l in sched.values() if name in l])
            print(f"{name:12}{ntasks}")


# janky setup, this information should be in a location shared with what the GUI uses.
WEEKDAYS = ['Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lørdag', 'Søndag']
TIMES = ['middag', 'aftensmad', 'kaffe']
def timeslot_order(p1, p2):
    d1, t1 = p1[0]
    d2, t2 = p2[0]
    if d1 != d2:
        return WEEKDAYS.index(d1) - WEEKDAYS.index(d2)
    else:
        return TIMES.index(t1) - TIMES.index(t2)

