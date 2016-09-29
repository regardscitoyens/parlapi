# -*- coding: utf-8 -*-
import collections

from flask import abort, jsonify, request, url_for


class PaginationResult(object):
    def __init__(self, items):
        self._items = items
        self._count = len(items)


class API(object):
    def __init__(self, ma, app):
        self.endpoints = {}
        self.ma = ma
        self.page_size = app.config['API_PAGE_SIZE'] or 10

    def listURL(self, table):
        return self.ma.AbsoluteURLFor('api_list', table=table)

    def detailURL(self, table):
        return self.ma.AbsoluteURLFor('api_detail', table=table, id='<id>')

    def nested(self, schema):
        return self.ma.Nested(schema)

    def nestedList(self, schema):
        return self.ma.List(self.ma.Nested(schema))

    @property
    def descriptions(self):
        descs = {k: v['description'] for k, v in self.endpoints.items()}
        return collections.OrderedDict(sorted(descs.items()))

    def endpoint(self, model, detail_schema, **kwargs):
        table = model.__tablename__

        query = kwargs.get('query', lambda: model.query)

        def detail_query(id):
            return query().filter_by(id=id)

        self.endpoints[table] = {
            'model': model,
            'detail_schema': self.add_list_url(detail_schema),
            'list_schema':
                self.add_pagination(kwargs.get('list_schema', detail_schema)),
            'detail_query': kwargs.get('detail_query', detail_query),
            'list_query': kwargs.get('list_query', query),
            'description': kwargs.get('description', table)
        }

    def add_list_url(self, schema):
        table = schema.Meta.model.__tablename__

        _fields = ()
        if len(schema.Meta.fields):
            _fields = schema.Meta.fields + ('_list',)

        class ListSchema(schema):
            class Meta(schema.Meta):
                fields = _fields

            _list = self.listURL(table)

        return ListSchema

    def add_pagination(self, schema):
        class PaginatedSchema(self.ma.Schema):
            _count = self.ma.Int()
            _items = self.ma.List(self.ma.Nested(schema))
            _prev = self.ma.Str()
            _next = self.ma.Str()

        return PaginatedSchema

    def get_endpoint_or_404(self, table, detail=False):
        if table not in self.endpoints:
            abort(404)

        endpoint = self.endpoints[table]
        prefix = 'detail' if detail else 'list'
        return endpoint['%s_schema' % prefix], endpoint['%s_query' % prefix]

    def get_list_or_404(self, table):
        schema, get_query = self.get_endpoint_or_404(table)

        page = int(request.args.get('page') or 1)
        size = int(request.args.get('page_size') or self.page_size)

        data = get_query().paginate(page, size)
        obj = {
            '_count': data.total,
            '_items': data.items,
        }

        if data.has_prev:
            obj['_prev'] = '%s?page=%d%s' % (
                url_for('api_list', table=table, _external=True),
                data.prev_num,
                '&page_size=%d' % size if size != self.page_size else ''
            )

        if data.has_next:
            obj['_next'] = '%s?page=%d%s' % (
                url_for('api_list', table=table, _external=True),
                data.next_num,
                '&page_size=%d' % size if size != self.page_size else ''
            )

        result = schema().dump(obj)
        return jsonify(result.data)

    def get_detail_or_404(self, table, id):
        schema, get_query = self.get_endpoint_or_404(table, True)

        item = get_query(id).one()
        try:
            pass
        except:
            abort(404)

        result = schema().dump(item)
        return jsonify(result.data)

    def setup_routes(self, app, prefix='/rest/'):
        if not prefix.endswith('/'):
            prefix = '%s/' % prefix

        if not prefix.startswith('/'):
            prefix = '/%s' % prefix

        @app.route('%s<table>/' % prefix)
        def api_list(table):
            return self.get_list_or_404(table)

        @app.route('%s<table>/<id>' % prefix)
        def api_detail(table, id):
            return self.get_detail_or_404(table, id)
