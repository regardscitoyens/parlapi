# -*- coding: utf-8 -*-

from flask import render_template, url_for

from .models import Job


def setup_routes(app, rest_api):
    rest_prefix = '/rest/'
    rest_api.setup_routes(app, rest_prefix)

    @app.route('/')
    def home():
        jobs = Job.query.all()
        return render_template('index.html', rest_api=rest_api.descriptions,
                               rest_prefix=rest_prefix, jobs=jobs)
