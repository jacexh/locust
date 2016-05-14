# -*- coding: utf-8 -*-

from StringIO import StringIO
from flask import jsonify, make_response
from locust.web import app
import pygal


@app.route("/svg/rps.svg")
def rps_svg():
    bar_chart = pygal.Bar()
    bar_chart.add('Fibonacci', [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55])
    return bar_chart.render_response()
