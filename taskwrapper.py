""" ---------------------------------------------------------------------------

    taskwrapper.py - Implementation for TaskWrapper class

    Copyright 2017, John Ferguson

    Licensed under GPLv3, see LICENSE for full details

--------------------------------------------------------------------------- """

import json
import os
import subprocess
import threading
import time

class TaskWrapper:
    """
    Wrapper for TaskWarrior. Spawns a thread, and calls change_cb whenever
    updates are made to TaskWarrior (either externally, or through TaskHUD
    application).
    """
    def __init__(self, task_cmd="task", task_path="~/.task", change_cb=None):
        # name of TaskWarrior executable in users PATH
        self.task_cmd = task_cmd

        # path to TaskWarrior data directory
        self.task_path = task_path

        # callback for when TaskWarrior database gets updated
        self.change_cb = change_cb

        # paths to TaskWarrior files where changes indicate an update
        backlog_path = self.task_path + "/backlog.data"
        pending_path = self.task_path + "/pending.data"

        # store full paths to these files
        self.backlog_path = os.path.expanduser(backlog_path)
        self.pending_path = os.path.expanduser(pending_path)

        # if files can't be found, raise an exception
        if not os.path.isfile(self.backlog_path):
            raise Exception("couldn't find {}".format(self.backlog_path))
        if not os.path.isfile(self.pending_path):
            raise Exception("couldn't find {}".format(self.pending_path))

        # store the last update time for these files at initialization
        self.backlog_mtime = os.path.getmtime(self.backlog_path)
        self.pending_mtime = os.path.getmtime(self.pending_path)

        # local database of records from TaskWarrior
        self.task_db = []

        # update the local task database
        self.update_task_db()

        # spawn monitoring thread as daemon (so that it closes automatically
        # when TaskHUD application is closed)
        self.t = threading.Thread(target=self.watch_thread)
        self.t.setDaemon(True)
        self.t.start()

    def task_db_changed(self):
        """
        returns True if task database has changed since last check
        """
        # Assume no changes have occured
        changed = False

        # Check modification timestamps for TaskWarrior files
        new_backlog_mtime = os.path.getmtime(self.backlog_path)
        new_pending_mtime = os.path.getmtime(self.pending_path)

        if self.backlog_mtime != new_backlog_mtime:
            # Backlog was modified
            self.backlog_mtime = new_backlog_mtime
            changed = True

        if self.pending_mtime != new_pending_mtime:
            # Pending tasks were modified
            self.pending_mtime = new_pending_mtime
            changed = True

        return changed


    def update_task_db(self):
        """
        calls TaskWarrior to update local task database
        """
        # Call TaskWarrior and have it export all records (JSON)
        task_proc = subprocess.Popen(
            [self.task_cmd, "export", "."], stdout=subprocess.PIPE
        )

        (output, err) = task_proc.communicate()
        exit_code = task_proc.wait()

        # TODO: handle errors and exit codes

        # Convert to a list of JSON
        task_json = json.loads(output)
        # Store locally
        self.task_db = task_json

        # Call the change callback if available and callable
        if self.change_cb is not None:
            if callable(self.change_cb):
                self.change_cb()

    def watch_thread(self):
        """
        Keep checking file timestamps, and update local database if files
        ever change.
        """
        while True:
            if self.task_db_changed():
                self.update_task_db()

            # TODO: make interval user-configurable
            time.sleep(0.25)

