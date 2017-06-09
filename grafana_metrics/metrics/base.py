# coding: utf-8
from __future__ import unicode_literals


class MetricData(object):

    def __init__(self, name, value, tags=None, time=None, fields=None):
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
        self.fields = fields

    def __unicode__(self):
        metric_string = "name={name}, value={value}, time={time}".format(
            name=self.name,
            value=self.value,
            time=self.time
        )
        if self.tags:
            metric_string += ",{}".format(",".join(self.tags))
        if self.fields:
            metric_string += ",{}".format(",".join(["%s=%s" % (k, v) for k, v in self.fields.items()]))
        return metric_string

    def to_influx(self):
        row = {
            'measurement': self.name,
            'value': self.value,
        }
        if self.tags:
            row['tags'] = self.tags
        if self.time:
            row['time'] = self.time
        if self.fields:
            row['fields'] = self.fields
        return row


class Metric(object):

    def __init__(self, measurement, tags=None, interval=60, timeout=2):
        self.measurement = measurement
        self.tags = tags
        self.interval = int(interval)

    def collect(self):
        raise NotImplemented
