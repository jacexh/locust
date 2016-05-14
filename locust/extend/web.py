# -*- coding: utf-8 -*-

from StringIO import StringIO
from flask import jsonify, make_response
from locust.web import app
import pygal


@app.route("/svg/rps.svg")
def rps_svg():
    return jsonify(dict(code="100"))
