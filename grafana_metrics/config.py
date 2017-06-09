# coding: utf-8
from __future__ import unicode_literals

from collections import defaultdict
from ConfigParser import ConfigParser


class ConfigValidationException(Exception):
    pass


class ConfigItems(object):

    def __init__(self, items):
        self.items = items

    def get(self, key, default=None):
        val = self.getlist(key)
        if val:
            return val[-1]
        else:
            return default

    def getlist(self, key):
        return [v.strip() for k, v in self.items if k == key]

    def to_dict(self):
        data = defaultdict(list)
        for k, v in self.items:
            if v:
                data[k].append(v)

        for k in data:
            if len(data[k]) == 1:
                data[k] = data[k][0]
        return dict(data)


class Config(ConfigParser, object):

    NO_SECTION_ERORR = 'No section "%(section)s"'
    NO_PARAM = 'Not set prameter "%(parameter)s" in section "[%(section)s]"'
    NO_METRICS = 'There are no sections with a metric, please add a header to the config "[Metric: MyMetricName]"'

    def items(self, section):
        items = super(self.__class__, self).items(section)
        return ConfigItems(items)

    def validate(self):
        self._validate_engine()
        self._validate_metrics()

    def _validate_engine(self):
        sections = self.sections()
        if "Engine" not in sections:
            raise ConfigValidationException(self.NO_SECTION_ERORR % 'Engine')
        engine = self.items('Engine')
        engine_type = engine.get('type')
        if not engine_type:
            raise ConfigValidationException(self.NO_PARAM % {'parameter': 'type', 'section': 'Engine'})
        if engine_type == 'InfluxDB':
            self._validate_engine_influx()
        else:
            raise ConfigValidationException('Unknown engine type "{}"'.format(engine_type))

    def _validate_engine_influx(self):
        engine = self.items('Engine')
        if not engine.get('host'):
            raise ConfigValidationException(self.NO_PARAM % {'parameter': 'host', 'section': 'Engine'})
        if not engine.get('port'):
            raise ConfigValidationException(self.NO_PARAM % {'parameter': 'port', 'section': 'Engine'})
        if not engine.get('database'):
            raise ConfigValidationException(self.NO_PARAM % {'parameter': 'database', 'section': 'Engine'})

    def _validate_metrics(self):
        sections = [section for section in self.sections() if section.startswith('Metric:')]
        if not sections:
            raise ConfigValidationException(self.NO_METRICS)

        for section in sections:
            metric = self.items(section)
            if not metric.get('type'):
                raise ConfigValidationException(self.NO_PARAM % {'parameter': 'type', 'section': section})
