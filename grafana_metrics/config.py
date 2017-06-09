# coding: utf-8
from __future__ import unicode_literals

from ConfigParser import ConfigParser


class ConfigValidationException(Exception):
    pass


class Config(ConfigParser):

    NO_SECTION_ERORR = 'No section "%(section)s"'
    NO_PARAM = 'Not set prameter "%(parameter)s" in section "[%(section)s]"'
    NO_METRICS = 'There are no sections with a metric, please add a header to the config "[Metric: MyMetricName]"'

    def validate(self):
        self._validate_engine()
        self._validate_metrics()

    def _validate_engine(self):
        sections = self.sections()
        if "Engine" not in sections:
            raise ConfigValidationException(self.NO_SECTION_ERORR % 'Engine')
        engine = dict(self.items('Engine'))
        if not engine.get('type'):
            raise ConfigValidationException(self.NO_PARAM % {'parameter': 'type', 'section': 'Engine'})
        if engine['type'] == 'InfluxDB':
            self._validate_engine_influx()
        else:
            raise ConfigValidationException('Unknown engine type "{}"'.format(engine['type']))

    def _validate_engine_influx(self):
        engine = dict(self.items('Engine'))
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
            metric = dict(self.items(section))
            if not metric.get('type'):
                raise ConfigValidationException(self.NO_PARAM % {'parameter': 'type', 'section': section})
