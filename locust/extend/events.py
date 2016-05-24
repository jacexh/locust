# -*- coding: utf-8 -*-

import time
try:
    import simplejson as json
except (ImportError, SyntaxError):
    import json
from locust import events as ori_events
import pika


class Globals(object):

    rabbit_channel = None
    rabbit_exchange = None


class _Config(object):

    def __init__(self):
        self._report_to_rabbit = 0

    def enable_report_to_rabbit(self, exchange, url=None, **kwargs):
        if Globals.rabbit_channel is None:
            if url:
                connection = pika.BlockingConnection(pika.URLParameters(url))
            elif kwargs:
                connection = pika.BlockingConnection(pika.ConnectionParameters(**kwargs))
            else:
                raise ValueError("RabbitMQ connection parameters needed")
            Globals.rabbit_channel = connection.channel()
        if Globals.rabbit_exchange is None:
            Globals.rabbit_exchange = exchange

        if not self._report_to_rabbit:
            ori_events.request_success += report_to_rabbit
            self._report_to_rabbit = 1

    def disable_report_to_rabbit(self):
        self._report_to_rabbit = 0
        ori_events.request_success -= report_to_rabbit


def report_to_rabbit(request_type, name, response_time, response_length, **kwargs):
    response = {
        "measurement": "locust",
        "tags": {"name": name, "request_type": request_type},
        "timestamp": int(time.time()*1000),
        "fields": {"response_time": response_time, "response_length": response_length}
    }
    if Globals.rabbit_exchange and Globals.rabbit_channel:
        Globals.rabbit_channel.basic_publish(Globals.rabbit_exchange, "", body=json.dumps(response))


config = _Config()
