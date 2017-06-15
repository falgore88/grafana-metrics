# coding: utf-8
from __future__ import unicode_literals


class MetricData(object):

    def __init__(self, name, fields, tags=None, *args, **kwargs):
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

    def __repr__(self):
        return self.__unicode__().encode("utf-8")


class Metric(object):

    TYPE = None

    def __init__(self, measurement, tags=None, interval=60, timeout=2, *args, **kwargs):
        self.measurement = measurement
        self.tags = tags or {}
        self.interval = int(interval)
        self.timeout = int(timeout) if timeout else None

    def collect(self):
        raise NotImplemented

    def get_name(self):
        return "%s(%s)" % (self.measurement, self.TYPE)

    def __repl__(self):
        return self.get_name()

    def __unicode__(self):
        return self.get_name()
