# -*- coding: utf-8 -*-

from flask_graphql import GraphQLView

from .schema import schema


class API(object):
    def setup_routes(self, app, prefix='/graphql/'):
        if not prefix.endswith('/'):
            prefix = '%s/' % prefix

        if not prefix.startswith('/'):
            prefix = '/%s' % prefix

        app.add_url_rule(
            prefix,
            view_func=GraphQLView.as_view(
                'graphql',
                schema=schema,
                graphiql=True
            )
        )
