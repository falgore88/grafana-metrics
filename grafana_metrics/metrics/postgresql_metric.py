# coding=utf-8
from __future__ import unicode_literals

from .base import Metric, MetricData
from copy import copy


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
                metrics = []
                cursor.execute(self.query)
                cursor_description = cursor.description
                many_res = [dict(zip([column[0] for column in cursor_description], row)) for row in cursor.fetchall()]
                for res in many_res:
                    tags = copy(self.tags)
                    for k in tags:
                        if k in res:
                            tags[k] = res[k]
                    metrics.append(MetricData(
                        name=self.measurement,
                        tags=tags,
                        fields=res
                    ))
                return metrics
