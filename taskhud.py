from taskwrapper import TaskWrapper

def callback():
    print("task DB updated")

if __name__ == "__main__":
    task_wrapper = TaskWrapper(change_cb = callback)

    while True:
        pass

