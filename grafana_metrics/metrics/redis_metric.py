# coding=utf-8
from __future__ import unicode_literals

from base import Metric, MetricData


class Redis(Metric):

    TYPE = 'redis'

    def __init__(self, *args, **kwargs):
        from redis import Redis as Client

        super(self.__class__, self).__init__(*args, **kwargs)
        self.host = kwargs.get('host')
        self.port = kwargs.get('port')
        self.password = kwargs.get('password')
        try:
            self.client = Client(
                host=self.host or 'localhost',
                port=int(self.port or 6379),
                password=self.password
            )
        except Exception as e:
            raise Exception("Redis connect failed: {}".format(str(e)))

    def collect(self):
        data = self.client.info('Memory')
        for db, db_info in self.client.info("Keyspace").items():
            for key, val in db_info.items():
                data["{}_{}".format(db, key)] = val
        return [MetricData(
            name=self.measurement,
            tags=self.tags,
            fields=data
        )]
