# coding: utf-8
from __future__ import unicode_literals

import logging
from threading import Thread
from multiprocessing.dummy import Pool as ThreadPool, TimeoutError
from contextlib import closing


class MetricThread(Thread):
    def __init__(self, metric, callback, *args, **kwargs):
        super(MetricThread, self).__init__(*args, **kwargs)
        self.daemon = True
        self.metric = metric
        self.callback = callback

    def run(self):
        try:
            with closing(ThreadPool(1)) as pool:
                async_res = pool.apply_async(self.metric.collect)
                try:
                    collected_data = async_res.get(self.metric.timeout)
                    if collected_data:
                        for metric_data in collected_data:
                            logging.info('The metric "{}" is collected: {}'.format(self.metric.get_name(), unicode(metric_data)))
                    else:
                        logging.info('The metric "{}" no data'.format(self.metric.get_name()))
                    self.callback(self.metric, collected_data)
                except TimeoutError:
                    logging.warning('The metric "{}" collect timeout {} sec'.format(self.metric.get_name(), self.metric.timeout))
            pool.terminate()
        except Exception as e:
            print e
            logging.warning('The metric "{}" collect error: {}'.format(self.metric.get_name(), str(e)))
        self.callback(self.metric, [])
