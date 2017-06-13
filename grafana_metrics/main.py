#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals

import logging
import logging.handlers
import os
import signal
import sys
from argparse import ArgumentParser
from ConfigParser import Error
from datetime import datetime
from time import sleep

from config import Config, ConfigValidationException
from engines.influx import InfluxDB
from metrics import CPU, Disk, Memory, Nginx


def signal_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


class GMetricsException(Exception):
    pass


class GMetrics(object):

    LOG_FORMAT = '%(asctime)s | %(name)s | %(levelname)s | %(message)s'

    def __init__(self):
        args = self.parse_arguments()
        self.validate_args(args)
        self.args = args
        self.config_file = self.args.config

        config = Config()
        try:
            config.read(self.config_file)
            config.validate()
        except ConfigValidationException as e:
            raise GMetricsException("Error validate config: {}".format(str(e)))
        except Error as e:
            raise GMetricsException("Error parsing config: {}".format(str(e)))

        self.config = config

        try:
            logging.basicConfig(level=logging.INFO, format=self.LOG_FORMAT)
            if self.args.log:
                formatter = logging.Formatter(self.LOG_FORMAT)
                handler = logging.handlers.RotatingFileHandler(self.args.log)
                handler.setFormatter(formatter)
                logging.root.addHandler(handler)
        except IOError as e:
            raise GMetricsException("Error set log file: {}".format(str(e)))

        self.logger = logging.getLogger("GMetrics")

    def get_metrics(self):
        sections = [section for section in self.config.sections() if section.startswith("Metric:")]
        metrics = {}
        for section_name in sections:
            section_params = self.config.items(section_name).to_dict()
            metric_type = section_params.pop('type')
            metric_name = section_name.replace('Metric:', '').strip()
            metric_key = "%s(%s)" % (metric_name, metric_type)
            tags = section_params.pop('tag', [])
            if not isinstance(tags, list):
                tags = [tags]
            try:
                metric = self.get_metric_by_type(metric_type, metric_name, section_params, tags)
                metrics[metric_key] = metric
            except Exception as e:
                self.logger.warning('Error initialize metric "{}": {}'.format(metric_key, str(e)))
        return metrics

    def get_metric_by_type(self, metric_type, metric_name, params, tags_data):

        tags = {}
        if tags_data:
            for tag_d in tags_data:
                key, val = tag_d.split("=")
                tags[key.strip()] = val.strip()

        if metric_type == 'cpu':
            return CPU(metric_name, tags, **params)
        elif metric_type == 'memory':
            return Memory(metric_name, tags, **params)
        elif metric_type == 'disk':
            return Disk(metric_name, tags, **params)
        elif metric_type == 'nginx':
            return Nginx(metric_name, tags, **params)
        raise GMetricsException('Unknown metric type "{}"'.format(metric_type))

    def get_engine(self):
        engine_config = self.config.items('Engine')
        engine_type = engine_config.get('type')
        engine = None
        if engine_type == 'InfluxDB':
            params = dict(
                host=engine_config.get('host'),
                port=engine_config.get('port'),
                database=engine_config.get('database'),
                username=engine_config.get('username') or None,
                password=engine_config.get('password') or None
            )
            engine = InfluxDB(**params)
        if not engine:
            raise GMetricsException('Unknown engine type "{}"'.format(engine_type))
        else:
            return engine_type, params, engine

    def parse_arguments(self):
        parser = ArgumentParser()
        parser.add_argument(
            '--config',
            help='Patch to config.ini',
            type=str
        )
        parser.add_argument(
            '--log',
            help='Path to log file',
            type=str
        )
        return parser.parse_args()

    def validate_args(slef, args):
        if not args.config:
            raise GMetricsException("No set config file, please run program with parameter --config=patch_to_config.ini")
        if not os.path.isfile(args.config):
            raise GMetricsException("Config file not found, check the correctness of the path in --config")

    def run(self):
        self.logger.info("Initializing")
        engine_type, engine_params, engine = self.get_engine()
        self.logger.info('Find engine "{}" with options "{}"'.format(engine_type, ",".join(["%s=%s" % (k, v) for k, v in engine_params.items()])))

        metrics = self.get_metrics()
        for metric_name, metric in metrics.items():
            self.logger.info('Find metric "{}" interval={} tags={}'.format(metric_name, metric.interval, ",".join(["%s=%s" % (k, v) for k, v in metric.tags.items()])))
        metric_interval_data = {}

        while True:
            metric_collected_data = []
            for metric_name, metric in metrics.items():
                if not metric_interval_data.get(metric_name) or (datetime.now() - metric_interval_data[metric_name]).seconds >= metric.interval:
                    try:
                        collected_data = metric.collect()
                        if collected_data:
                            for metric_data in collected_data:
                                self.logger.info('The metric "{}" is collected: {}'.format(metric_name, unicode(metric_data)))
                            metric_collected_data.extend(collected_data)
                        else:
                            self.logger.info('The metric "{}" no data'.format(metric_name))
                    except Exception as e:
                        print e
                        self.logger.warning('Metric "{}" collection failed: {}'.format(metric_name, str(e)))
                    metric_interval_data[metric_name] = datetime.now()
            try:
                if metric_collected_data:
                    engine.send(metric_collected_data)
                    self.logger.info("Sending {} metrics to the database success".format(len(metric_collected_data)))
            except Exception as e:
                self.logger.warning("Sending metrics to the database failed: {}".format(str(e)))
            sleep(1)


def main(*args, **kwargs):
    try:
        GMetrics().run()
    except GMetricsException as e:
        print "\x1b[1;37;41m{}\x1b[0m".format(str(e))


if __name__ == '__main__':
    main()
