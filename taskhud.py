""" ---------------------------------------------------------------------------

    taskhud.py - Entry point for TaskHUD application

    Copyright 2017, John Ferguson

    Licensed under GPLv3, see LICENSE for full details

--------------------------------------------------------------------------- """

from curses import wrapper
from cwrapper import CursesHud
from datetime import datetime, timezone
from taskwrapper import TaskWrapper

# TODO: move to separate module
def t_date(s):
    """
    TaskWarrior provides times as UTC timestamps in ISO 8601
    """
    year   = int(s[0:4])
    month  = int(s[4:6])
    day    = int(s[6:8])

    hour   = int(s[9:11])
    minute = int(s[11:13])
    second = int(s[13:15])

    # This is UTC time
    ts = datetime(year, month, day, hour, minute, second)

    # Convert to local time
    local_time = ts.replace(tzinfo=timezone.utc).astimezone(tz=None)
    # Convert to ISO display format, and remove timezone offset
    iso_format = local_time.isoformat(sep=" ")[:-6]

    return iso_format

# TODO: move to separate module
def t_tags(s):
    """
    TaskWarrior provides tags as list of strings, render without "[" + "]"
    """
    return ", ".join(s)

# TODO: move to separate module
def t_urgency(s):
    """
    Align urgency scores on decimal place, limit to 2 significant digits
    """
    return "{:>6.2f}".format(s)

def run_gui(screen, task_wrapper):
    """
    Called by curses wrapper. Sets up HUD before running mainloop
    """
    # HUD object
    hud = CursesHud(screen)

    # Use "uuid" as unique key for records
    hud.set_unique_key("uuid")

    # link TaskWrapper callback to update the HUD
    def update_hud_records():
        hud.add_record(task_wrapper.task_db)

    task_wrapper.change_cb = update_hud_records

    # Add all tasks stored in task_wrapper at startup
    # TODO: these should be refreshed continuously and asynchronously
    for task in task_wrapper.task_db:
        hud.add_record(task)

    # These keys will be shown in bottom panel (too wide for main display)
    hud.set_extra_info("uuid")
    hud.set_extra_info("depends")
    hud.set_extra_info("annotations")
    hud.set_extra_info("modified")

    # These value types need to be reformatted for display
    ## Dates from ISO 8601 UTC -> Local time
    hud.set_translation("due", t_date)
    hud.set_translation("entry", t_date)
    hud.set_translation("end", t_date)
    hud.set_translation("start", t_date)
    hud.set_translation("scheduled", t_date)
    
    ## Tags converted from ["x", "y", "z"] -> "x, y, z"
    hud.set_translation("tags", t_tags)
    
    ## Align urgency scores on decimal place, 2 significant digits
    hud.set_translation("urgency", t_urgency)

    # Run the HUD's main loop
    hud.mainloop()

if __name__ == "__main__":
    # Entry point

    # Start up TaskWarrior monitoring thread
    task_wrapper = TaskWrapper()

    # Start ncurses, and pass screen object to function that sets up HUD
    wrapper(run_gui, task_wrapper)

