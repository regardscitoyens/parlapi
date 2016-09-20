# -*- coding: utf-8 -*-

from flask import Flask


def setup_app(name):
    # Create app
    app = Flask(name)

    # Load config
    app.config.from_object('parlapi.config.CurrentConfig')

    # Setup DB
    from .models import db
    db.init_app(app)

    # Setup API
    from .api import setup_api
    api = setup_api(app)

    # Setup routes
    from .routes import setup_routes
    setup_routes(app, api)

    return app
