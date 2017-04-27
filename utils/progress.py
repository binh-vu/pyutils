#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from datetime import timedelta

"""
    Help print beautiful progress (percentage, total, estimate time, etc.)
"""
class Progress(object):

    """
        @param total int
    """
    def __init__(self, total):
        self.total = total
        self.current = 0
        self.last_time = None
        self.average_task_time = 0

    def start(self):
        self.current = 0
        return self.report()

    def finish_one(self):
        # since from the Progress constructed to the first task finish is unknown,
        # so finish time can only be estimate correctly from second task.
        if self.current >= 1: # when self.current is 1, this already second task
            one_task_time = float(time.time() - self.last_time)
            if self.current == 1:
                self.average_task_time = one_task_time
            else:
                self.average_task_time = float(self.average_task_time * self.current + one_task_time) / (self.current + 1)

        self.current += 1
        self.last_time = time.time()
        return self.report()

    def report(self):
        eta = 'N/A'
        if self.current > 1:
            eta = round((self.total - self.current) * self.average_task_time, 3)
            eta = str(timedelta(seconds=eta))[:-3]

        return '%.2f%% (%s/%s). ETA: %s' % (
            self.current * 100.0 / self.total,
            self.current, self.total, eta
        )
    

if __name__ == '__main__':
    import random

    tasks = range(20)
    progress = Progress(len(tasks))

    for task in tasks:
        print progress.finish_one()
        # time.sleep(random.random())
        time.sleep(1)
