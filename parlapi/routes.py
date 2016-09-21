# -*- coding: utf-8 -*-

from flask import render_template, url_for

from .models import Job


def setup_routes(app, api):
    api_prefix = '/api/'
    api.setup_routes(app, api_prefix)

    @app.route('/')
    def home():
        jobs = Job.query.all()
        return render_template('index.html', api=api.descriptions,
                               api_prefix=api_prefix, jobs=jobs)
