# coding=utf-8
from __future__ import unicode_literals

import psutil
from base import Metric, MetricData


class Memory(Metric):

    def collect(self):
        virtual_memory = psutil.virtual_memory()
        return [MetricData(
            name=self.measurement,
            tags=self.tags,
            fields={
                "total": virtual_memory.total,
                "available": virtual_memory.available,
                "percent": virtual_memory.percent,
                "used": virtual_memory.used,
                "free": virtual_memory.free,
                "active": virtual_memory.active,
                "inactive": virtual_memory.inactive,
                "buffers": virtual_memory.buffers,
                "cached": virtual_memory.cached,
                "shared": virtual_memory.shared
            }

        )]
