# coding: utf-8
from __future__ import unicode_literals

import psutil
from base import Metric, MetricData
from datetime import datetime


class CPU(Metric):

    def collect(self):
        metrics = []
        for cpu_num, cpu_percent in enumerate(psutil.cpu_percent(interval=1, percpu=True), start=1):
            metrics.append(MetricData(
                name=self.measurement,
                value=cpu_percent,
                time=datetime.now(),
                tags=self.tags,
                fields={
                    "cpu_num": cpu_num
                }
            ))
        return metrics
