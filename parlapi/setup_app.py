# -*- coding: utf-8 -*-

import os

from flask import Flask


def setup_app(name):
    # Create app
    app = Flask(name)

    # Load config
    config_obj = os.environ.get('PARLAPI_CONFIG',
                                'parlapi.config.DefaultConfig')
    app.config.from_object(config_obj)

    # Setup DB
    from .models import db
    db.init_app(app)

    # Setup REST API
    from .rest.setup import setup_api
    rest_api = setup_api(app)

    # Setup routes
    from .routes import setup_routes
    setup_routes(app, rest_api)

    return app
