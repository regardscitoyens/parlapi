# -*- coding: utf-8 -*-

from flask import abort, jsonify
from flask_marshmallow import Marshmallow

from .models import Regime, Legislature, Organe


class API(object):
    def __init__(self, schemas):
        self.schemas = schemas
        self.tables = {i['model'].__tablename__: i for i in schemas}
        self.descriptions = {i['model'].__tablename__: i['description']
                             for i in schemas}

    def get_schema_or_404(self, table):
        if table not in self.tables:
            abort(404)

        item = self.tables[table]
        model = item['model']
        schema = item['schema']
        list_schema = item.get('list_schema', schema)

        return list_schema, schema, model

    def get_list_or_404(self, table):
        list_schema, detail_schema, model = self.get_schema_or_404(table)
        items = model.query.all()
        result = list_schema(many=True).dump(items)
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

    # API helpers

    def detailURL(table):
        return ma.AbsoluteURLFor('api_detail', table=table, id='<id>')

    def nested(schema):
        return ma.Nested(schema)

    def nestedList(schema):
        return ma.List(ma.Nested(schema))

    # Base schemas (for use in lists)

    class RegimeBaseSchema(ma.ModelSchema):
        class Meta:
            model = Regime
            fields = ('nom', '_url')

        _url = detailURL('regimes')

    class LegislatureBaseSchema(ma.ModelSchema):
        class Meta:
            model = Legislature
            fields = ('numero', '_url')

        _url = detailURL('legislatures')

    class OrganeBaseSchema(ma.ModelSchema):
        class Meta:
            model = Organe
            fields = ('libelle', '_url')

        _url = detailURL('organes')

    # Detailed schemas

    class RegimeDetailSchema(RegimeBaseSchema):
        class Meta(RegimeBaseSchema.Meta):
            fields = ()

        legislatures = nestedList(LegislatureBaseSchema)
        organes = nestedList(OrganeBaseSchema)

    class LegislatureDetailSchema(LegislatureBaseSchema):
        class Meta(LegislatureBaseSchema.Meta):
            fields = ()

        regime = nested(RegimeBaseSchema)
        organes = nestedList(OrganeBaseSchema)

    class OrganeDetailSchema(OrganeBaseSchema):
        class Meta(OrganeBaseSchema.Meta):
            fields = ()

        regime = nested(RegimeBaseSchema)
        legislature = nested(LegislatureBaseSchema)

    # API creation

    return API([
        {
            'model': Regime,
            'description': u'Régimes politiques',
            'schema': RegimeDetailSchema,
            'list_schema': RegimeBaseSchema
        },
        {
            'model': Legislature,
            'description': u'Législatures',
            'schema': LegislatureDetailSchema,
            'list_schema': LegislatureBaseSchema
        },
        {
            'model': Organe,
            'description': u'Organes (ministères, commissions, organismes...)',
            'schema': OrganeDetailSchema,
            'list_schema': OrganeBaseSchema
        },
    ])
