# -*- coding: utf-8 -*-


def setup_routes(app):
    @app.route('/')
    def hello():
        return 'Hi!'
