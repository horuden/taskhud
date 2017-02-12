import json
import os
import subprocess
import threading
import time

class TaskWrapper:
    """
    Wrapper for TaskWarrior
    """
    def __init__(self, task_cmd="task", task_path="~/.task", change_cb=None):
        self.task_cmd = task_cmd
        self.task_path = task_path
        self.change_cb = change_cb

        backlog_path = self.task_path + "/backlog.data"
        pending_path = self.task_path + "/pending.data"

        self.backlog_path = os.path.expanduser(backlog_path)
        self.pending_path = os.path.expanduser(pending_path)

        if not os.path.isfile(self.backlog_path):
            raise Exception("couldn't find {}".format(self.backlog_path))
        if not os.path.isfile(self.pending_path):
            raise Exception("couldn't find {}".format(self.pending_path))

        self.backlog_mtime = os.path.getmtime(self.backlog_path)
        self.pending_mtime = os.path.getmtime(self.pending_path)

        self.task_db = []

        self.update_task_db()

        self.t = threading.Thread(target=self.watch_thread)
        self.t.setDaemon(True)
        self.t.start()

    def task_db_changed(self):
        """
        returns True if task database has changed since last check
        """
        changed = False

        new_backlog_mtime = os.path.getmtime(self.backlog_path)
        new_pending_mtime = os.path.getmtime(self.pending_path)

        if self.backlog_mtime != new_backlog_mtime:
            self.backlog_mtime = new_backlog_mtime
            changed = True

        if self.pending_mtime != new_pending_mtime:
            self.pending_mtime = new_pending_mtime
            changed = True

        return changed


    def update_task_db(self):
        """
        calls TaskWarrior to update local task database
        """
        task_proc = subprocess.Popen(
            ["task", "export", "."], stdout=subprocess.PIPE
        )

        (output, err) = task_proc.communicate()
        exit_code = task_proc.wait()

        # TODO: handle errors and exit codes

        task_json = json.loads(output)

        self.task_db = task_json

        if self.change_cb is not None:
            if callable(self.change_cb):
                self.change_cb()

    def watch_thread(self):
        while True:
            if self.task_db_changed():
                self.update_task_db()

            time.sleep(0.25)

