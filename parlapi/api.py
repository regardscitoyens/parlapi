# -*- coding: utf-8 -*-

import collections

from flask import abort, jsonify, request, url_for
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import joinedload


from .models import (
    Acte,
    Acteur,
    Document,
    Dossier,
    Legislature,
    Mandat,
    Organe,
    Regime,
    Theme
)


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

    class ThemeBaseSchema(ma.ModelSchema):
        class Meta:
            model = Theme
            fields = ('theme', '_url')

        _url = api.detailURL('themes')

    class DocumentBaseSchema(ma.ModelSchema):
        class Meta:
            model = Document
            fields = ('titre', '_url')

        _url = api.detailURL('documents')

    class DossierBaseSchema(ma.ModelSchema):
        class Meta:
            model = Dossier
            fields = ('titre', 'procedure_libelle', '_url')

        _url = api.detailURL('dossiers')

    class ActeBaseSchema(ma.ModelSchema):
        class Meta:
            model = Acte
            fields = ('libelle', '_url')

        _url = api.detailURL('actes')

    # Semi-detailed schemas (for use in some relations)

    class MandatListSchema(MandatBaseSchema):
        class Meta(MandatBaseSchema.Meta):
            fields = MandatBaseSchema.Meta.fields + ('acteur', 'organes')

        organes = api.nestedList(OrganeBaseSchema)
        acteur = api.nested(ActeurBaseSchema)

    class MandatActeurSchema(MandatBaseSchema):
        class Meta(MandatBaseSchema.Meta):
            fields = MandatBaseSchema.Meta.fields + ('organes',)

        organes = api.nestedList(OrganeBaseSchema)

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
        organes = api.nestedList(OrganeBaseSchema)

    class ThemeDetailSchema(ThemeBaseSchema):
        class Meta(ThemeBaseSchema.Meta):
            fields = ()

        documents = api.nestedList(DocumentBaseSchema)

    class DocumentDetailSchema(DocumentBaseSchema):
        class Meta(DocumentBaseSchema.Meta):
            fields = ()

    class DossierDetailSchema(DossierBaseSchema):
        class Meta(DossierBaseSchema.Meta):
            fields = ()

    class ActeDetailSchema(ActeBaseSchema):
        class Meta(ActeBaseSchema.Meta):
            fields = ()

    # API creation

    def regime_detail_query(id):
        return Regime.query \
            .options(joinedload('organes')) \
            .options(joinedload('legislatures')) \
            .filter_by(id=id)

    api.endpoint(
        Regime,
        RegimeDetailSchema,
        list_schema=RegimeBaseSchema,
        description=u'Régimes politiques',
        detail_query=regime_detail_query
    )

    def legislature_detail_query(id):
        return Legislature.query \
            .options(joinedload('organes')) \
            .options(joinedload('regime')) \
            .filter_by(id=id)

    api.endpoint(
        Legislature,
        LegislatureDetailSchema,
        list_schema=LegislatureBaseSchema,
        description=u'Législatures',
        detail_query=legislature_detail_query
    )

    def organe_detail_query(id):
        return Organe.query \
            .options(joinedload('legislature')) \
            .options(joinedload('regime')) \
            .options(joinedload('mandats').joinedload('acteur')) \
            .filter_by(id=id)

    api.endpoint(
        Organe,
        OrganeDetailSchema,
        list_schema=OrganeBaseSchema,
        description=u'Organes (ministères, commissions, organismes...)',
        detail_query=organe_detail_query
    )

    def acteur_detail_query(id):
        return Acteur.query \
            .options(joinedload('mandats').joinedload('organes')) \
            .filter_by(id=id)

    api.endpoint(
        Acteur,
        ActeurDetailSchema,
        list_schema=ActeurBaseSchema,
        description=u'Acteurs (ministres, parlementaires...)',
        detail_query=acteur_detail_query
    )

    def mandat_query():
        return Mandat.query \
            .options(joinedload('organes')) \
            .options(joinedload('acteur'))

    api.endpoint(
        Mandat,
        MandatDetailSchema,
        list_schema=MandatListSchema,
        description=u'Mandats',
        query=mandat_query
    )

    def theme_detail_query(id):
        return Theme.query \
            .options(joinedload('documents')) \
            .filter_by(id=id)

    api.endpoint(
        Theme,
        ThemeDetailSchema,
        list_schema=ThemeBaseSchema,
        description=u'Thèmes',
        detail_query=theme_detail_query
    )

    api.endpoint(
        Document,
        DocumentDetailSchema,
        list_schema=DocumentBaseSchema,
        description=u'Documents législatifs'
    )

    api.endpoint(
        Dossier,
        DossierDetailSchema,
        list_schema=DossierBaseSchema,
        description=u'Dossiers législatifs',
    )

    api.endpoint(
        Acte,
        ActeDetailSchema,
        list_schema=ActeBaseSchema,
        description=u'Actes législatifs',
    )

    return api
