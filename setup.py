#!/usr/bin/env python
from __future__ import with_statement
from setuptools import setup, find_packages


VERSION = "0.0.2"

setup(
    name='grafana-metrics',
    description="",
    version=VERSION,
    url='https://github.com/falgore88/grafana-metrics',
    author='Evgeniy Titov',
    author_email='falgore88@gmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'gmetrics = grafana_metrics.main:main',
        ]
    },
)
