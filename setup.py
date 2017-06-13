#!/usr/bin/env python
from __future__ import with_statement
from setuptools import setup, find_packages


VERSION = "0.0.15"

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
