# coding: utf-8
from __future__ import unicode_literals

import psutil
from base import Metric, MetricData
from datetime import datetime


class CPU(Metric):

    def __init__(self, measurement, engine, tags=None):
        self.measurement = measurement
        self.tags = tags
        self.engine = engine

    def collect(self):
        metrics = []
        for cpu_num, cpu_percent in enumerate(psutil.cpu_percent(interval=1, percpu=True), start=1):
            metrics.append(MetricData(
                name=self.measurement,
                value=cpu_percent,
                time=datetime.now()
            ))
        return metrics

    def send(self):
        metrics = self.collect()
        return self.engine.send(metrics)
