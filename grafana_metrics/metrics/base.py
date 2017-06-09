# coding: utf-8
from __future__ import unicode_literals


class MetricData(object):

    def __init__(self, name, value, tags=None, time=None):
        """
        :param name: string
        :param value: any
        :param tags: list
        :param time: datetime
        """
        self.name = name
        self.value = value
        self.tags = tags
        self.time = time

    def to_influx(self):
        row = {
            'measurement': self.name,
            'value': self.value,
        }
        if self.tags:
            row['tags'] = self.tags
        if self.time:
            row['time'] = self.time
        return row


class Metric(object):

    def collect(self):
        raise NotImplemented
