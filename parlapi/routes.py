# -*- coding: utf-8 -*-

from flask import abort, jsonify


def setup_routes(app, api):
    api.setup_routes(app)

    @app.route('/')
    def hello():
        return 'Bienvenue sur ParlAPI :)'
