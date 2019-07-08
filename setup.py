#!/usr/bin/env python
# coding=utf-8
from __future__ import with_statement, unicode_literals

from setuptools import find_packages, setup

VERSION = "1.1.0"

setup(
    name='grafana-metrics',
    description="",
    version=VERSION,
    url='https://github.com/falgore88/grafana-metrics',
    author='Evgeniy Titov',
    author_email='falgore88@gmail.com',
    packages=find_packages(),
    install_requires=[
        'influxdb==4.1.1',
        'psutil==5.2.2'
    ],
    entry_points={
        'console_scripts': [
            'gmetrics = grafana_metrics.main:main',
        ]
    },
)
