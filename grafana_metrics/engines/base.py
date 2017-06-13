# coding: utf-8
from __future__ import unicode_literals


class Engine(object):

    def send(self, metrics):
        """
        :param metrics: MetricData
        """
        raise NotImplemented
