# coding: utf-8
from __future__ import unicode_literals

import os
from argparse import ArgumentParser
from ConfigParser import Error
from config import Config, ConfigValidationException
from engines import InfluxDB


class GMetricsException(Exception):
    pass


class GMetrics(object):

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

    def get_engine(self, engine_type):
        if engine_type == 'influxdb':
            return InfluxDB

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
        self.parse_arguments()


def main(*args, **kwargs):
    try:
        GMetrics().run()
    except GMetricsException as e:
        print "\x1b[1;37;41m{}\x1b[0m".format(str(e))


if __name__ == '__main__':
    main()
