# -*- coding: utf-8 -*-

import time
try:
    import simplejson as json
except (ImportError, SyntaxError):
    import json
from locust import events as ori_events


__all__ = ["config"]


class Globals(object):

    rabbit_channel = None
    rabbit_exchange = None
    influx_client = None


class _Config(object):

    @staticmethod
    def enable_report_to_rabbit(exchange, url=None, **kwargs):
        import pika

        if Globals.rabbit_channel is None:
            if url:
                connection = pika.BlockingConnection(pika.URLParameters(url))
            elif kwargs:
                connection = pika.BlockingConnection(pika.ConnectionParameters(**kwargs))
            else:
                raise ValueError("RabbitMQ connection parameters needed")

            Globals.rabbit_channel = connection.channel()
            Globals.rabbit_exchange = exchange
            ori_events.request_success += report_to_rabbit

    @staticmethod
    def disable_report_to_rabbit():
        ori_events.request_success -= report_to_rabbit
        Globals.rabbit_exchange = None
        Globals.rabbit_channel = None

    @staticmethod
    def enable_report_to_influx(dsn=None, **kwargs):
        import influxdb

        if Globals.influx_client is None:
            if dsn:
                Globals.influx_client = influxdb.InfluxDBClient.from_DSN(dsn, **kwargs)
            elif kwargs:
                Globals.influx_client = influxdb.InfluxDBClient(**kwargs)
            else:
                raise ValueError("InfluxDB connection parameters needed")

            ori_events.request_success += report_to_influx

    @staticmethod
    def disable_report_to_influx():
        Globals.influx_client = None
        ori_events.request_success -= report_to_influx


def response_to_dict(request_type, name, response_time, response_length, **kwargs):
    return {
        "measurement": "locust",
        "tags": {"name": name, "request_type": request_type},
        "timestamp": int(time.time() * 1000),
        "fields": {"response_time": response_time, "response_length": response_length}
    }


def report_to_rabbit(request_type, name, response_time, response_length, **kwargs):
    if Globals.rabbit_exchange and Globals.rabbit_channel:
        Globals.rabbit_channel.basic_publish(Globals.rabbit_exchange, "", body=json.dumps(response_to_dict(
            request_type, name, response_time, response_length, **kwargs)))


def report_to_influx(request_type, name, response_time, response_length, **kwargs):
    if Globals.influx_client:
        Globals.influx_client.write_points(
            [response_to_dict(request_type, name, response_time, response_length, **kwargs)])


config = _Config()
