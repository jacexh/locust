# -*- coding: utf-8 -*-

from itertools import chain
from flask import jsonify, make_response
from locust.web import app, _sort_stats
from locust import runners
import pygal


@app.route("/chart/distribution.svg")
def rps_svg():
    line_chart = pygal.Bar()
    line_chart.x_labels = ["50%", "66%", "75%", "80%", "90%", "95%", "98%", "99%", "100%"]

    for s in _sort_stats(runners.locust_runner.request_stats):
        if s.num_requests:
            line_chart.add(s.name,
                           [s.get_response_time_percentile(0.5),
                            s.get_response_time_percentile(.66),
                            s.get_response_time_percentile(.75),
                            s.get_response_time_percentile(.8),
                            s.get_response_time_percentile(.9),
                            s.get_response_time_percentile(.95),
                            s.get_response_time_percentile(.98),
                            s.get_response_time_percentile(.99),
                            s.max_response_time])
        else:
            line_chart.add(s.name, [None, None, None, None, None, None, None, None, None])
    return line_chart.render_response()


@app.route("/report.html")
def report_html():
    return """<!DOCTYPE html>
<html>
  <head>
    <!-- ... -->
  </head>
  <body>
    <figure>
      <embed type="image/svg+xml" src="/chart/distribution.svg" />
    </figure>
  </body>
</html>
"""
