# coding: utf-8
from __future__ import unicode_literals


class MetricData(object):

    def __init__(self, name, fields, tags=None):
        """
        :param name: string
        :param value: any
        :param tags: list
        :param time: datetime
        """
        self.name = name
        self.tags = tags or {}
        self.fields = fields

    def __unicode__(self):
        metric_string = "name=%s" % self.name
        if self.tags:
            metric_string += ",{}".format(",".join(["%s=%s" % (k, v) for k, v in self.tags.items()]))
        metric_string += ",{}".format(",".join(["%s=%s" % (k, v) for k, v in self.fields.items()]))
        return metric_string

    def to_influx(self):
        row = {
            'measurement': self.name,
        }
        if self.tags:
            row['tags'] = self.tags
        if self.fields:
            row['fields'] = self.fields
        return row


class Metric(object):

    def __init__(self, measurement, tags=None, interval=60, timeout=2):
        self.measurement = measurement
        self.tags = tags or {}
        self.interval = int(interval)

    def collect(self):
        raise NotImplemented
