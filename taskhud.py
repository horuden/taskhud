from curses import wrapper
from cwrapper import CursesHud
from taskwrapper import TaskWrapper


def callback():
    pass

def run_gui(screen):
    hud = CursesHud(screen)

    for task in task_wrapper.task_db:
        hud.add_record(task)

    hud.mainloop()

if __name__ == "__main__":
    task_wrapper = TaskWrapper(change_cb = callback)

    wrapper(run_gui)

