"""
test.py - first pass, seeing what can be done

problems: need to resize columns so data doesn't fall off edge of terminal
"""

import curses
from curses import wrapper
import json
from subprocess import Popen, PIPE

tw_proc = Popen(["task", "export", "."], stdout=PIPE)
(output, err) = tw_proc.communicate()
exit_code = tw_proc.wait()

json = json.loads(output)

def t_field_date(s):
    year   = s[0:4]
    month  = s[4:6]
    day    = s[6:8]

    hour   = s[9:11]
    minute = s[11:13]
    second = s[13:15]

    return "{}-{}-{} {}:{}:{}".format(year, month, day, hour, minute, second)

def t_field_priority(s):
    return {
        "H": "HIGH",
        "M": "MED",
        "L": "LOW"
    }[s]

field_transforms = [
    (
        ["due", "entry", "modified", "scheduled", "end"],
        t_field_date
    ),
    (
        ["priority"],
        t_field_priority
    )
]

field_widths = {}

for n, record in enumerate(json):
    for k,v in record.items():
        for transform in field_transforms:
            if k in transform[0]:
                json[n][k] = transform[1](v)

        if k not in field_widths:
            field_widths[k] = 0

        if len(str(json[n][k])) > field_widths[k]:
            field_widths[k] = len(str(json[n][k]))
import sys
print(field_widths)
print(sum(field_widths.values()))
#sys.exit(1)

potential_columns = ["id"]

for record in json:
    print("task ID: {}".format(record['id']))
    for k,v in record.items():
        print("  {}: {}".format(k, v))

        if k not in potential_columns:
            potential_columns += [k]

print("potential columns: {}".format(", ".join(potential_columns)))

def main(s):
    task_selected = 0

    s.clear()

    pairs = []

    for i in range(0,curses.COLORS):
        try:
            curses.init_pair(i + 1, i, 0)
        except:
            s.addstr(curses.LINES - 2, 0, "error {}".format(i))

    #for i in range(0, curses.COLORS):
    #    s.addstr(curses.LINES - 3, i, "x", curses.color_pair(i + 1))
   
    while True:

        col_width = curses.COLS // len(potential_columns)

        acc = 0
        for n, title in enumerate(potential_columns):
            col_width = min(field_widths[title], 20)

            s.addstr(0, acc , "{:<{width}}".format(title[:col_width], width=col_width))
            s.addstr(1, acc , "-" * (col_width) + " ")

            acc += col_width
            acc += 1

        for n, task in enumerate(json):
            for nf, field in enumerate(potential_columns):
                a = 0

                if n == task_selected:
                    a = curses.A_REVERSE

                a += curses.color_pair(n + 1)

                col_width = min(field_widths[field], 16)
                if field in task:
                    s.addstr(2 + n, col_width * nf, "{:<{width}}".format(str(task[field])[:col_width -1], width=col_width), a)
                else:
                    s.addstr(2 + n, col_width * nf, "{:<{width}}".format(" " * col_width, width=col_width), a)

        
        s.addstr(curses.LINES - 1, 0, "{}".format(curses.COLORS))
                    

        s.refresh()

        c = s.getch()

        if c == curses.KEY_UP:
            task_selected = max(0, task_selected - 1)
        elif c == curses.KEY_DOWN:
            task_selected = min(len(json) - 1, task_selected + 1)

wrapper(main)
