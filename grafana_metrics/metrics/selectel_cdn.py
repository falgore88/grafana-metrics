# coding=utf-8
from __future__ import unicode_literals

import json
from copy import copy
from datetime import datetime, timedelta

import requests
from .base import Metric, MetricData


class SelectelCDN(Metric):
    TYPE = 'selectel_cdn'

    AUTH_URL = 'https://auth.selcdn.ru/'

    def __init__(self, *args, **kwargs):
        super(SelectelCDN, self).__init__(*args, **kwargs)

        self.login = kwargs.get('login')
        if not self.login:
            raise Exception("Login not set")

        self.password = kwargs.get('password')
        if not self.password:
            raise Exception("Password not set")

        self._token = None
        self._storage_url = None
        self._token_expire = None

    def authorization(self):
        response = requests.get(self.AUTH_URL, headers={
            'X-Auth-User': self.login,
            'X-Auth-Key': self.password
        })
        if response.status_code != 204:
            raise Exception('Could not log in. Status code: {}'.format(response.status_code))

        self._token = response.headers['X-Auth-Token']
        self._storage_url = response.headers['X-Storage-Url']
        self._token_expire = datetime.now() + timedelta(seconds=int(response.headers['X-Expire-Auth-Token']))

    def get_storage_info(self):
        if not self._token or not self._storage_url or (self._token_expire - datetime.now()).total_seconds() < 300:
            self.authorization()

        response = requests.get(self._storage_url + "?format=json", headers={
            'X-Auth-Token': self._token,
        })
        response.raise_for_status()
        return json.loads(response.text)

    def collect(self):
        data = []
        total = {
            'count': 0,
            'bytes': 0
        }
        for container in self.get_storage_info():
            tags = copy(self.tags)
            tags.update({
                "container": container['name']
            })
            data.append(MetricData(
                name=self.measurement,
                tags=tags,
                fields={
                    "count": container['count'],
                    'bytes': container['bytes']
                }
            ))
            total['count'] += int(container['count'])
            total['bytes'] += int(container['bytes'])

        tags = copy(self.tags)
        tags['container'] = 'total'
        data.append(MetricData(
            name=self.measurement,
            tags=tags,
            fields=total
        ))
        return data
