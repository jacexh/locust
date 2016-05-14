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

    for s in chain(_sort_stats(runners.locust_runner.request_stats),
                   [runners.locust_runner.stats.aggregated_stats("Total", full_request_history=True)]):
        if s.num_requests:
            data = s.percentile(tpl='%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s')
            formatted = data.split("\t")
            line_chart.add(s.name, formatted[2:])
        else:
            line_chart.add(s.name, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    return line_chart.render_response()


@app.route("/report.html")
def report_html():
    return """"<!DOCTYPE html>
<html>
  <head>
    <!-- ... -->
  </head>
  <body>
    <figure>
      <embed type="image/svg+xml" src="/chart/distribution.svg" />
    </figure>
  </body>
</html>"""

