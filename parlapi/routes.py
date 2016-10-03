# -*- coding: utf-8 -*-

import datetime
import os

from flask import render_template, url_for
import humanize

from .models import Job


def setup_routes(app, rest_api, graphql_api):
    rest_prefix = '/rest/'
    rest_api.setup_routes(app, rest_prefix)

    graphql_prefix = '/graphql/'
    graphql_api.setup_routes(app, graphql_prefix)

    @app.template_filter('humanize_seconds')
    def humanize_seconds(seconds):
        if not seconds:
            return ''

        humanize.i18n.activate('fr')
        return humanize.naturaldelta(datetime.timedelta(seconds=seconds))

    @app.template_filter('humanize_datetime')
    def humanize_datetime(date):
        if not date:
            return ''

        humanize.i18n.activate('fr')
        return humanize.naturaltime(date)

    @app.template_filter('basename')
    def basename(path):
        return os.path.basename(path)

    @app.route('/')
    def home():
        piwik = None
        if app.config['PIWIK_HOST']:
            piwik = {
                'host': app.config['PIWIK_HOST'],
                'id': app.config['PIWIK_ID']
            }

        return render_template(
            'index.html',
            piwik=piwik,
            rest_api=rest_api.descriptions,
            rest_prefix=rest_prefix,
            graphql_prefix=graphql_prefix,
            jobs=Job.query.all()
        )
