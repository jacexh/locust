# -*- coding: utf-8 -*-

from itertools import chain
from locust.web import app, _sort_stats
from locust import runners
import pygal


@app.route("/chart/distribution.svg")
def distribution_svg():
    chart = pygal.Bar(title='Response Time Distribution', legend_at_bottom=True, legend_at_bottom_columns=1)
    chart.x_labels = ["50%", "66%", "75%", "80%", "90%", "95%", "98%", "99%", "100%"]

    for s in _sort_stats(runners.locust_runner.request_stats):
        if s.num_requests:
            chart.add(s.name, [
                s.get_response_time_percentile(0.5),
                s.get_response_time_percentile(.66),
                s.get_response_time_percentile(.75),
                s.get_response_time_percentile(.8),
                s.get_response_time_percentile(.9),
                s.get_response_time_percentile(.95),
                s.get_response_time_percentile(.98),
                s.get_response_time_percentile(.99),
                s.max_response_time
            ])
    return chart.render_response()


@app.route("/chart/statistics.svg")
def statistics_svg():
    chart = pygal.Bar(title="Request Statistics", legend_at_bottom=True, legend_at_bottom_columns=1)
    chart.x_labels = ["Median", "Average", "Min", "Max"]

    for s in _sort_stats(runners.locust_runner.request_stats):
        if s.num_requests:
            chart.add(s.name, [
                s.median_response_time,
                s.avg_response_time,
                s.min_response_time or 0,
                s.max_response_time
            ])
    return chart.render_response()


@app.route("/report.html")
def report_html():
    html = """<!DOCTYPE html>
<html>
  <head>
    <title>Locust Test Report</title>
  </head>
  <body>
  <div style="text-align:center">
    <figure>
      <embed type="image/svg+xml" src="/chart/distribution.svg" height="600"/>
    </figure>
    <figure>
        <embed type="image/svg+xml" src="/chart/statistics.svg" height="600"/>
        </figure>
</div>
  </body>
</html>"""
    return html
