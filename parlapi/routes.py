# -*- coding: utf-8 -*-

from flask import redirect


def setup_routes(app):

    @app.errorhandler(404)
    def error404(e):
        return redirect('/')

    @app.route('/')
    def hello():
        return 'Hi!'
