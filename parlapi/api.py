# -*- coding: utf-8 -*-

from flask import abort, jsonify, request, url_for
from flask_marshmallow import Marshmallow

from .models import Regime, Legislature, Organe, Acteur, Mandat


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
        return {k: v['description'] for k, v in self.endpoints.items()}

    def endpoint(self, model, detail_schema, **kwargs):
        table = model.__tablename__

        self.endpoints[table] = {
            'model': model,
            'detail_schema': self.add_list_url(detail_schema),
            'list_schema': self.add_pagination(kwargs.get('list_schema',
                                                          detail_schema)),
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

    def get_schema_or_404(self, table):
        if table not in self.endpoints:
            abort(404)

        item = self.endpoints[table]
        model = item['model']
        detail_schema = item['detail_schema']
        list_schema = item['list_schema']

        return list_schema, detail_schema, model

    def get_list_or_404(self, table):
        list_schema, detail_schema, model = self.get_schema_or_404(table)

        page = int(request.args.get('page') or 1)
        size = int(request.args.get('page_size') or self.page_size)

        data = model.query.paginate(page, size)
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

        result = list_schema().dump(obj)
        return jsonify(result.data)

    def get_detail_or_404(self, table, id):
        list_schema, detail_schema, model = self.get_schema_or_404(table)

        item = model.query.get_or_404(id)

        result = detail_schema().dump(item)
        return jsonify(result.data)

    def setup_routes(self, app, prefix='/api/'):
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


def setup_api(app):
    ma = Marshmallow(app)
    api = API(ma, app)

    # Base schemas (for use in lists & some relations)

    class RegimeBaseSchema(ma.ModelSchema):
        class Meta:
            model = Regime
            fields = ('nom', '_url')

        _url = api.detailURL('regimes')

    class LegislatureBaseSchema(ma.ModelSchema):
        class Meta:
            model = Legislature
            fields = ('numero', '_url')

        _url = api.detailURL('legislatures')

    class OrganeBaseSchema(ma.ModelSchema):
        class Meta:
            model = Organe
            fields = ('libelle', 'type', '_url')

        _url = api.detailURL('organes')

    class ActeurBaseSchema(ma.ModelSchema):
        class Meta:
            model = Acteur
            fields = ('nom', 'prenom', '_url')

        _url = api.detailURL('acteurs')

    class MandatBaseSchema(ma.ModelSchema):
        class Meta:
            model = Mandat
            fields = ('qualite', '_url')

        _url = api.detailURL('mandats')

    # Semi-detailed schemas (for use in some relations)

    class MandatListSchema(MandatBaseSchema):
        class Meta(MandatBaseSchema.Meta):
            fields = MandatBaseSchema.Meta.fields + ('acteur', 'organe',)
        organe = api.nested(OrganeBaseSchema)
        acteur = api.nested(ActeurBaseSchema)

    class MandatActeurSchema(MandatBaseSchema):
        class Meta(MandatBaseSchema.Meta):
            fields = MandatBaseSchema.Meta.fields + ('organe',)

        organe = api.nested(OrganeBaseSchema)

    class MandatOrganeSchema(MandatBaseSchema):
        class Meta(MandatBaseSchema.Meta):
            fields = MandatBaseSchema.Meta.fields + ('acteur',)

        acteur = api.nested(ActeurBaseSchema)

    # Detailed schemas

    class RegimeDetailSchema(RegimeBaseSchema):
        class Meta(RegimeBaseSchema.Meta):
            fields = ()

        legislatures = api.nestedList(LegislatureBaseSchema)
        organes = api.nestedList(OrganeBaseSchema)

    class LegislatureDetailSchema(LegislatureBaseSchema):
        class Meta(LegislatureBaseSchema.Meta):
            fields = ()

        regime = api.nested(RegimeBaseSchema)
        organes = api.nestedList(OrganeBaseSchema)

    class OrganeDetailSchema(OrganeBaseSchema):
        class Meta(OrganeBaseSchema.Meta):
            fields = ()

        legislature = api.nested(LegislatureBaseSchema)
        mandats = api.nestedList(MandatOrganeSchema)
        regime = api.nested(RegimeBaseSchema)

    class ActeurDetailSchema(ActeurBaseSchema):
        class Meta(ActeurBaseSchema.Meta):
            fields = ()

        mandats = api.nestedList(MandatActeurSchema)

    class MandatDetailSchema(MandatBaseSchema):
        class Meta(MandatBaseSchema.Meta):
            fields = ()

        acteur = api.nested(ActeurBaseSchema)
        organe = api.nested(OrganeBaseSchema)

    # API creation

    api.endpoint(
        Regime,
        RegimeDetailSchema,
        list_schema=RegimeBaseSchema,
        description=u'Régimes politiques'
    )

    api.endpoint(
        Legislature,
        LegislatureDetailSchema,
        list_schema=LegislatureBaseSchema,
        description=u'Législatures'
    )

    api.endpoint(
        Organe,
        OrganeDetailSchema,
        list_schema=OrganeBaseSchema,
        description=u'Organes (ministères, commissions, organismes...)'
    )

    api.endpoint(
        Acteur,
        ActeurDetailSchema,
        list_schema=ActeurBaseSchema,
        description=u'Acteurs (ministres, parlementaires...)'
    )

    api.endpoint(
        Mandat,
        MandatDetailSchema,
        list_schema=MandatListSchema,
        description=u'Mandats'
    )

    return api
