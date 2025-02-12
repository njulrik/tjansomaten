#!/usr/bin/env python3

import re

from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from model import *
from z3sched import schedule

from typing import List



root = Tk()
root.title("Tjansomaten v0.1")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)


def check_num(newval):
    return re.match("^[0-9]*$", newval) is not None and len(newval) <= 5


check_num_wrapper = (root.register(check_num), "%P")


class TimeslotInput(ttk.Frame):
    def __init__(self, parent, timeslot: Timeslot, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)

        self.timeslot_ = timeslot
        self.entry_val_ = StringVar()
        self.entry_ = ttk.Entry(
            self, validate="key", validatecommand=check_num_wrapper, width=6, textvariable=self.entry_val_)
        self.entry_val_.set(self.timeslot_.needed)
        self.entry_.state(["disabled"])
        self.entry_.grid(column=2, row=0, sticky=E)

        box_val = StringVar(value="disabled")
        self.box_ = ttk.Checkbutton(
            self,
            # text=timeslot.name,
            variable=box_val,
            onvalue="!disabled",
            offvalue="disabled",
            command=lambda: self.entry_.state([box_val.get()]),
        )
        self.box_.grid(column=0, row=0, sticky=W)

        self.columnconfigure(0, weight=1)

    def get_needed(self) -> int:
        return 0 if self.entry_.instate(["disabled"]) else int(self.entry_.get())

    def set_needed(self, val):
        self.entry_val_.set(val)

    def get_timeslot(self) -> Timeslot:
        self.timeslot_.needed = self.get_needed()
        return self.timeslot_


class CalendarInput(ttk.LabelFrame):
    WEEKDAYS = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]

    def __init__(self, parent):
        ttk.LabelFrame.__init__(self, parent, text="Vælg tjanser", padding="3 3 12 12")

        self.calendar: Dict[str, Dict[str, TimeslotInput]] = {}

        ttk.Label(self, text="Opvask middag").grid(column=0, row=1, sticky=W, padx=8)
        ttk.Label(self, text="Opvask aftensmad").grid(column=0, row=2, sticky=W, padx=8)
        ttk.Label(self, text="Opvask aftenkaffe").grid(
            column=0, row=3, sticky=W, padx=8
        )
        ttk.Separator(self, orient=VERTICAL).grid(column=1, row=0, rowspan=4)
        for col, day in enumerate(self.WEEKDAYS):
            col = col + 2
            ttk.Label(self, text=day).grid(column=col, row=0, sticky=W)
            middag = TimeslotInput(self, Timeslot(f"{day} middag", 6))
            aften = TimeslotInput(self, Timeslot(f"{day} aftensmad", 6))
            kaffe = TimeslotInput(self, Timeslot(f"{day} kaffe", 2))
            middag.grid(column=col, row=1, padx=5, pady=5, sticky=[N, S, E, W])
            aften.grid(column=col, row=2, padx=5, pady=5, ipadx=4, sticky=[N, S, E, W])
            kaffe.grid(column=col, row=3, padx=5, pady=5, ipadx=4, sticky=[N, S, E, W])

            self.calendar[day] = {"middag": middag, "aften": aften, "kaffe": kaffe}
        self.calendar['Lørdag']['middag'].set_needed(4)
        self.calendar['Søndag']['middag'].set_needed(4)

    def get_weekdays(self) -> List[Weekday]:
        lst = []
        for day, slots in self.calendar.items():
            middag = slots['middag']
            aften = slots['aften']
            kaffe = slots['kaffe']
            if not any([time.get_needed() > 0 for time in [middag, aften, kaffe]]):
                continue
            day = Weekday(day)
            day.middag = middag.get_timeslot()
            day.aften = aften.get_timeslot()
            day.kaffe = kaffe.get_timeslot()
            lst.append(day)

        return lst


class LabelledText(ttk.Frame):

    def __init__(self, parent, name, **kwargs):
        ttk.Frame.__init__(self, parent)
        self.label: ttk.Label = ttk.Label(self, text=name)
        self.text = Text(self, background="#FFFFFF", foreground="#000000", **kwargs)
        self.label.grid(row=0, column=0, sticky=[W, S])
        self.text.grid(row=1, column=0, sticky=W)

        self.columnconfigure(0, weight=1)

    def get_contents(self):
        return self.text.get("1.0", "end")


def run_schedule():
    names = [name.strip() for name in name_input.get_contents().split("\n")]
    names = [name for name in names if len(name) != 0]
    weekend_list = [name.strip() for name in weekend_input.get_contents().split("\n")]
    weekend_list = [name for name in weekend_list if len(name) != 0]

    timeslots = cal.get_weekdays()
    def has_weekend_day():
        days = [day.name for day in timeslots]
        return 'Lørdag' in days or 'Søndag' in days

    if has_weekend_day() and len(weekend_list) == 0:
        if not messagebox.askokcancel(title="Tom weekendliste",
                                  message="Der er ingen personer angivet i weekendlisten. Planlæg ud fra, at alle er der i weekenden?"):
            return

        weekend_list = [name for name in names]

    cons = []

    schedule(names, weekend_list, timeslots, cons)



logo = PhotoImage(file="sickicon.png")
logolabel = ttk.Label(mainframe, anchor='center')
logolabel['image'] = logo
logolabel.grid(row=0, column=0, columnspan=2, sticky=[N,S,E,W])

name_input = LabelledText(mainframe, "Personer", width=40, height=20)
name_input.grid(row=1, column=0, sticky=W)
# person names redacted
#name_input.text.insert('1.0', '\n'.join([]))

weekend_input = LabelledText(mainframe, "Tilstede i weekenden", width=40, height=20)
weekend_input.grid(row=1, column=1, sticky=E)
# person names redacted
#weekend_input.text.insert("1.0", '\n'.join([]))


#copy_to_weekend_input = ttk.Button(mainframe, text="Kopier fra navne", command=copy_names)

cal = CalendarInput(mainframe)
cal.grid(row=3, column=0, columnspan=2)

exec_button = ttk.Button(mainframe, text="Planlæg tjanser", command=run_schedule)
exec_button.grid(row=4, column=1, pady=6, sticky=[E, S])

root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(1, weight=1)

root.mainloop()
