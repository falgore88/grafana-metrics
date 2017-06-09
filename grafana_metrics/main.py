# coding: utf-8
from __future__ import unicode_literals

import logging
import logging.handlers
import os
from argparse import ArgumentParser
from ConfigParser import Error
from config import Config, ConfigValidationException
from engines import InfluxDB


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

    def get_engine(self):
        engine_config = dict(self.config.items('Engine'))
        engine = None
        if engine_config['type'] == 'InfluxDB':
            params = dict(
                host=engine_config['host'],
                port=engine_config['port'],
                database=engine_config['database'],
                username=engine_config.get('username') or None,
                password=engine_config.get('password') or None
            )
            engine = InfluxDB(**params)
        if not engine:
            raise GMetricsException('Unknown engine type "{}"'.format(engine_config['type']))
        else:
            return engine_config['type'], params, engine

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
            type=str,
            default='/var/log/gmetrics/gmetrics.log'
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



def main(*args, **kwargs):
    try:
        GMetrics().run()
    except GMetricsException as e:
        print "\x1b[1;37;41m{}\x1b[0m".format(str(e))


if __name__ == '__main__':
    main()
