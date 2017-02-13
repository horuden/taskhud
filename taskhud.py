from curses import wrapper
from cwrapper import CursesHud
from taskwrapper import TaskWrapper


def callback():
    pass

def t_date(s):
    year   = s[0:4]
    month  = s[4:6]
    day    = s[6:8]

    hour   = s[9:11]
    minute = s[11:13]
    second = s[13:15]

    return "{}-{}-{} {}:{}:{}".format(year, month, day, hour, minute, second)

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

