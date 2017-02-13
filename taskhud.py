from curses import wrapper
from cwrapper import CursesHud
from datetime import datetime, timezone
from taskwrapper import TaskWrapper

def callback():
    pass

def t_date(s):
    year   = int(s[0:4])
    month  = int(s[4:6])
    day    = int(s[6:8])

    hour   = int(s[9:11])
    minute = int(s[11:13])
    second = int(s[13:15])

    # This is UTC time
    ts = datetime(year, month, day, hour, minute, second)

    # This is why we can't have nice things
    return ts.replace(tzinfo=timezone.utc).astimezone(tz=None).isoformat(sep=" ")[:-6]

def t_tags(s):
    return ", ".join(s)

def t_urgency(s):
    return "{:>6.2f}".format(s)

def run_gui(screen):
    hud = CursesHud(screen)

    for task in task_wrapper.task_db:
        hud.add_record(task)

    hud.set_extra_info("uuid")
    hud.set_extra_info("depends")
    hud.set_extra_info("annotations")
    hud.set_extra_info("modified")

    hud.set_translation("due", t_date)
    hud.set_translation("entry", t_date)
    hud.set_translation("end", t_date)
    hud.set_translation("start", t_date)
    hud.set_translation("scheduled", t_date)
    
    hud.set_translation("tags", t_tags)
    
    hud.set_translation("urgency", t_urgency)

    hud.mainloop()

if __name__ == "__main__":
    task_wrapper = TaskWrapper(change_cb = callback)

    wrapper(run_gui)

