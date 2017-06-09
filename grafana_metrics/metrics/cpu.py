# coding: utf-8
from __future__ import unicode_literals

import psutil
from base import Metric, MetricData
from copy import copy

class CPU(Metric):

    def collect(self):
        metrics = []
        for cpu_num, cpu_percent in enumerate(psutil.cpu_percent(interval=1, percpu=True), start=1):
            tags = copy(self.tags)
            tags.update({
                "cpu_num": cpu_num
            })
            metrics.append(MetricData(
                name=self.measurement,
                tags=tags,
                fields={
                    "percent": cpu_percent
                }
            ))
        return metrics
