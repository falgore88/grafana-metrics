# coding=utf-8
from __future__ import unicode_literals

from base import Metric, MetricData


class PostgreSQL(Metric):

    TYPE = 'postgresql'

    def __init__(self, *args, **kwargs):
        super(PostgreSQL, self).__init__(*args, **kwargs)
        self.dsn = kwargs.get('dsn')
        if not self.dsn:
            raise Exception("DSN not set")

        self.query = kwargs.get('query')
        if not self.query:
            raise Exception("Query not set")

    def collect(self):
        import psycopg2
        with psycopg2.connect(self.dsn) as con:
            with con.cursor() as cursor:
                cursor.execute(self.query)
                res = dict(zip([column[0] for column in cursor.description], cursor.fetchone()))
                return [MetricData(
                    name=self.measurement,
                    tags=self.tags,
                    fields=res
                )]
