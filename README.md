# Tjansomaten

Project for rudimentary chore allocation, developed while at Testrup Højskole. Solves the problem of assigning chores needing multiple people per task and multiple tasks per person. 

Solution depends on `z3` for solving a SAT/SMT encoding of the problem. Features a simple frontend written in `tkinter` in `gui.py`.

If `z3` for Python is installed, simply run `python gui.py`. If `z3` is not installed, you can install it using `pip install -r requirements.txt` or `pip install z3-solver`.
