#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals

import logging
import logging.handlers
import os
import signal
import sys
from ConfigParser import Error
from argparse import ArgumentParser
from datetime import datetime
from multiprocessing import Lock
from time import sleep

from config import Config, ConfigValidationException
from engines.influx import InfluxDB
from metrics.base import Metric
from thread_utils import MetricThread
from utils import inheritors


def signal_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


class GMetricsException(Exception):
    pass


class GMetrics(object):
    LOG_FORMAT = '%(asctime)s | %(levelname)s | %(message)s'

    def __init__(self):
        args = self.parse_arguments()
        self.validate_args(args)
        self.args = args
        self.config_file = self.args.config
        self.metrics = {c.TYPE: c for c in inheritors(Metric)}
        self.engine = None
        self.lock = Lock()

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
        sections = [section for section in self.config.sections()
                    if section.startswith("Metric:")]
        metrics = {}
        for section_name in sections:
            section_params = self.config.items(section_name).to_dict()
            metric_type = section_params.pop('type')
            metric_name = section_name.replace('Metric:', '').strip()
            tags = section_params.pop('tag', [])
            if not isinstance(tags, list):
                tags = [tags]
            try:
                metric = self.get_metric_by_type(metric_type, metric_name, section_params, tags)
                metrics[metric.get_name()] = metric
            except Exception as e:
                self.logger.warning(
                    'Error initialize metric "{}": {}'.format(metric_name, str(e)))
        return metrics

    def get_metric_by_type(self, metric_type, metric_name, params, tags_data):

        tags = {}
        if tags_data:
            for tag_d in tags_data:
                key, val = tag_d.split("=")
                tags[key.strip()] = val.strip()

        metric = self.metrics.get(metric_type)
        if metric:
            return metric(metric_name, tags, **params)
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
            raise GMetricsException(
                'Unknown engine type "{}"'.format(engine_type))
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
            raise GMetricsException(
                "No set config file, please run program with parameter --config=patch_to_config.ini")
        if not os.path.isfile(args.config):
            raise GMetricsException(
                "Config file not found, check the correctness of the path in --config")

    def run(self):
        self.logger.info("Initializing")
        engine_type, engine_params, engine = self.get_engine()
        self.engine = engine
        self.logger.info('Find engine "{}" with options "{}"'.format(engine_type, ",".join(["%s=%s" % (k, v) for k, v in engine_params.items()])))

        metrics = self.get_metrics()
        for metric_name, metric in metrics.items():
            self.logger.info('Find metric "{}" interval={} tags={}'.format(
                metric_name, metric.interval, ",".join(["%s=%s" % (k, v) for k, v in metric.tags.items()])))
        metric_interval_data = {}

        def process_metric(metric, collected_data):
            self.lock.acquire()
            if collected_data:
                for metric_data in collected_data:
                    logging.info('The metric "{}" is collected: {}'.format(metric.get_name(), unicode(metric_data)))
                self.engine.send(collected_data)
            metric_interval_data[metric.get_name()] = datetime.now()
            self.lock.release()

        metric_threads = {}

        while True:
            metric_need_collect = []
            for metric_name, metric in metrics.items():
                if not metric_interval_data.get(metric_name) or (datetime.now() - metric_interval_data[metric_name]).seconds >= metric.interval:
                    metric_need_collect.append(metric)

            if metric_need_collect:
                for metric in metric_need_collect:
                    metric_name = metric.get_name()
                    if not metric_threads.get(metric_name) or not metric_threads[metric_name].is_alive():
                        thread = MetricThread(metric, process_metric)
                        thread.start()
                        metric_threads[metric_name] = thread
            sleep(1)


def main(*args, **kwargs):
    try:
        GMetrics().run()
    except GMetricsException as e:
        print "\x1b[1;37;41m{}\x1b[0m".format(str(e))


if __name__ == '__main__':
    main()
