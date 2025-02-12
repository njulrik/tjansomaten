#!/usr/bin/env python3

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Constraint:
    name: str
    timeslot: str
    avail: bool

    def __str__(self) -> str:
        return "!" if self.avail else "" + varname(self.timeslot, self.name)


@dataclass
class Timeslot:
    name: str
    needed: int  # count 0 means timeslot not included

    def __str__(self) -> str:
        return self.name


class Weekday:
    name: str
    # TODO maybe refactor to Dict[str,int], would like operator[] in that case
    middag: Timeslot
    aften: Timeslot
    kaffe: Timeslot

    def __init__(self, name, tasks: Optional[List[str]] = None):
        self.name = name
        if tasks is not None:
            self.middag = Timeslot(f"{name} middag", needed=6 if "middag" in tasks else 0)
            self.aften = Timeslot(f"{name} aften", needed=6 if "aften" in tasks else 0)
            self.kaffe = Timeslot(f"{name} kaffe", needed=2 if "kaffe" in tasks else 0)

    def needed(self) -> List[Timeslot]:
        return [ts for ts in [self.middag, self.aften, self.kaffe] if ts.needed > 0]


class Vartable:
    def __init__(self):
        self.stoi = {}
        self.itos = {}
        self.nextid = 0

    def put(self, s: str) -> int:
        if s not in self.stoi:
            self.nextid += 1
            self.stoi[s] = self.nextid
            self.itos[self.nextid] = s
        return self.stoi[s]

    def get(self, id: int) -> str:
        assert self.stoi[self.itos[id]] == id
        return self.itos[id]

    def var_to_str(self, var: str) -> str:
        return self.itos[int(var[1:])]

    def str_to_var(self, s: str) -> str:
        id = self.put(str(s))
        return f"x{id}"

    def has_var(self, var: str) -> bool:
        try:
            self.var_to_str(var)
        except:
            return False
        return True

    def cons_to_var(self, cons: Constraint) -> str:
        var_readable = varname(cons.timeslot, cons.name)
        var = self.str_to_var(var_readable)
        print(f"{var=}\t{var_readable=}")
        return ('!' if not cons.avail else '') + var


SEPERATOR = '$'
def varname(timeslot, name):
    return f"{timeslot}{SEPERATOR}{name}"

def get_name(var):
    return var[var.rfind(SEPERATOR) + len(SEPERATOR_) :]

def get_timeslot(var):
    return var[: var.rfind(SEPERATOR)]
