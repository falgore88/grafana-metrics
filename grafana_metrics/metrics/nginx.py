# coding=utf-8
from __future__ import unicode_literals

import codecs
import os
import re
from collections import defaultdict
from hashlib import md5

from base import Metric, MetricData
from grafana_metrics.utils import reverse_readline


class Nginx(Metric):

    TYPE = 'nginx'

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.status_re = kwargs.get('status_re')
        try:
            self.status_re = re.compile(self.status_re, re.I | re.M | re.U)
        except re.error as e:
            raise Exception('Parameter "status_re" {}'.format(str(e)))

        self.access_log_path = kwargs.get('access_log_path')
        if not os.path.isfile(self.access_log_path):
            raise Exception('access_log not found by path "{}"'.format(self.access_log_path))

        self.last_read_row_hash = None

    def get_row_hash(self, row):
        return md5(row).hexdigest()

    def collect(self):
        with codecs.open(self.access_log_path) as fh:
            row_generator = reverse_readline(fh)
            if not self.last_read_row_hash:
                row = next(row_generator)
                self.last_read_row_hash = self.get_row_hash(row)
                return []
            else:
                first_row_hash = None
                data = defaultdict(int)
                while True:
                    try:
                        row = next(row_generator)
                    except StopIteration:
                        break
                    row_hash = self.get_row_hash(row)
                    if not first_row_hash:
                        first_row_hash = row_hash
                    if row_hash == self.last_read_row_hash:
                        break
                    match = self.status_re.match(row)
                    if match:
                        status = int(match.groups()[-1])
                        data[status] += 1
                        data['{}xx'.format(unicode(status)[0])] += 1
                        data['total'] += 1
            self.last_read_row_hash = first_row_hash
            if data:
                return [MetricData(
                    name=self.measurement,
                    tags=self.tags,
                    fields=dict(data)
                )]
            else:
                return []
