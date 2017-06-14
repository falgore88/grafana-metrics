# coding=utf-8
from __future__ import unicode_literals

import psutil
from base import Metric, MetricData


class Disk(Metric):

    TYPE = 'disk'

    def __init__(self, *args, **kwargs):
        super(Disk, self).__init__(*args, **kwargs)
        self.path = kwargs.get('path', '/')

    def collect(self):
        disk_data = psutil.disk_usage(self.path)
        return [MetricData(
            name=self.measurement,
            tags=self.tags,
            fields={
                "total": disk_data.total,
                "used": disk_data.used,
                "free": disk_data.free,
                "percent": disk_data.percent
            }
        )]
