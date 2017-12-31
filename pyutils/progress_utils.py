#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from datetime import timedelta, datetime


class Progress(object):
    """
        Help print beautiful progress (percentage, total, estimate time, etc.)
    """

    def __init__(self, total: int, start_time=False, current_time=False, eta=True, time_per_task=True, total_time=True, ms_threshold=1) -> None:
        self.total_time = total_time
        self.time_per_task = time_per_task
        self.eta = eta
        self.current_time = current_time
        self.start_time = start_time
        self.ms_threshold = ms_threshold  # convert to ms if average task time less than this number, otherwise using default: HH:MM:SS format

        self.total: int = total
        self.current: int = 0
        self.start_time: datetime = None
        self.last_time: float = None
        self.average_task_time: float = 0

    def start(self):
        self.current = 0
        self.start_time = datetime.now()
        return self.report()

    def finish_one(self):
        # since from the Progress constructed to the first task finish is unknown,
        # so finish time can only be estimate correctly from second task.
        if self.current >= 1:  # when self.current is 1, it's already second task
            one_task_time = float(time.time() - self.last_time)
            if self.current == 1:
                self.average_task_time = one_task_time
            else:
                self.average_task_time = float(self.average_task_time * self.current + one_task_time) / (
                    self.current + 1)

        self.current += 1
        self.last_time = time.time()
        return self.report()

    def report(self):
        report_str = []

        if self.start_time:
            report_str.append('Start time: ' + self.start_time.strftime('%Y-%m-%d %H:%M:%S'))

        if self.current_time:
            current_time_str = 'Current time: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            report_str.append(current_time_str)

        if self.time_per_task:
            task_time_str = 'Time per task: N/A'
            if self.current > 1:
                task_time_str = round(self.average_task_time, 3)
                if task_time_str <= self.ms_threshold:
                    task_time_str = "%d ms" % (task_time_str * 1000)
                else:
                    task_time_str = str(timedelta(seconds=task_time_str))[:-3]
                task_time_str = 'Time per task: ' + task_time_str
            report_str.append(task_time_str)

        if self.eta:
            eta_str = 'N/A'
            if self.current > 1:
                eta_str = round((self.total - self.current) * self.average_task_time, 3)
                eta_str = str(timedelta(seconds=eta_str))[:-3]
            eta_str = 'ETA: ' + eta_str
            report_str.append(eta_str)

        if self.total_time:
            total_time_str = 'Total time: ' + str(datetime.now() - self.start_time)[:-3]
            report_str.append(total_time_str)

        report_str.append(" " * 15)  # to clear out possible left out characters

        return '%.2f%% (%s/%s). %s' % (self.current * 100.0 / self.total, self.current, self.total,
                                       '. '.join(report_str))

    def summary(self):
        start_time = self.start_time
        current_time = self.current_time
        eta = self.eta
        total_time = self.total_time
        time_per_task = self.time_per_task

        self.start_time = True
        self.current_time = True
        self.eta = False
        self.total_time = True
        self.time_per_task = True

        report = "SUMMARY: " + self.report()

        self.start_time = start_time
        self.current_time = current_time
        self.eta = eta
        self.total_time = total_time
        self.time_per_task = time_per_task

        return report


class Timer(object):
    def __init__(self, time_unit: str='s') -> None:
        self.total_time = 0
        self.count = 0
        self.start_time = None
        self.time_unit_str = time_unit
        self.time_unit = {'s': 1, 'ms': 1000}[time_unit]

    def reset(self) -> 'Timer':
        self.total_time = 0
        self.count = 0
        self.start_time = time.time()
        return self

    def start(self) -> 'Timer':
        self.start_time = time.time()
        return self

    def lap(self) -> 'Timer':
        self.total_time = self.total_time + (time.time() - self.start_time)
        self.start_time = time.time()
        self.count += 1
        return self

    def get_average_time(self, precision=4):
        return '%.{0}f %s'.format(precision) % (self.get_raw_average_time() * self.time_unit, self.time_unit_str)

    def get_raw_average_time(self):
        return float(self.total_time) / self.count

    def get_total_time(self, precision=4):
        return '%.{0}f %s'.format(precision) % (self.time_unit * self.total_time, self.time_unit_str)

    def report(self, precision=4):
        return "%s times: %s (average: %s)" % (self.count, self.get_total_time(precision),
                                               self.get_average_time(precision))


class EmpiricalExpectation(object):
    def __init__(self) -> None:
        self.total = 0.0
        self.count = 0

    def reset(self):
        self.total = 0.0
        self.count = 0

    def observe(self, value):
        self.total += value
        self.count += 1

    def get_expectation(self, precision=4):
        return '%.{0}f s'.format(precision) % (self.get_raw_expectation())

    def get_raw_expectation(self):
        return self.total / self.count
