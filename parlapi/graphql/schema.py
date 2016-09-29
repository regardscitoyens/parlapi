# -*- coding: utf-8 -*-

import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from ..models import (
    Acte as ActeModel,
    Acteur as ActeurModel,
    Document as DocumentModel,
    Dossier as DossierModel,
    Legislature as LegislatureModel,
    Mandat as MandatModel,
    Organe as OrganeModel,
    Regime as RegimeModel,
    Theme as ThemeModel,
)


class Acte(SQLAlchemyObjectType):
    class Meta:
        model = ActeModel
        interfaces = (relay.Node,)


class Acteur(SQLAlchemyObjectType):
    class Meta:
        model = ActeurModel
        interfaces = (relay.Node,)


class Document(SQLAlchemyObjectType):
    class Meta:
        model = DocumentModel
        interfaces = (relay.Node,)


class Dossier(SQLAlchemyObjectType):
    class Meta:
        model = DossierModel
        interfaces = (relay.Node,)


class Legislature(SQLAlchemyObjectType):
    class Meta:
        model = LegislatureModel
        interfaces = (relay.Node,)


class Mandat(SQLAlchemyObjectType):
    class Meta:
        model = MandatModel
        interfaces = (relay.Node,)


class Organe(SQLAlchemyObjectType):
    class Meta:
        model = OrganeModel
        interfaces = (relay.Node,)


class Regime(SQLAlchemyObjectType):
    class Meta:
        model = RegimeModel
        interfaces = (relay.Node,)


class Theme(SQLAlchemyObjectType):
    class Meta:
        model = ThemeModel
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    all_actes = SQLAlchemyConnectionField(Acte)
    all_acteurs = SQLAlchemyConnectionField(Acteur)
    all_documents = SQLAlchemyConnectionField(Document)
    all_dossiers = SQLAlchemyConnectionField(Dossier)
    all_legislatures = SQLAlchemyConnectionField(Legislature)
    all_mandats = SQLAlchemyConnectionField(Mandat)
    all_organes = SQLAlchemyConnectionField(Organe)
    all_regimes = SQLAlchemyConnectionField(Regime)
    all_themes = SQLAlchemyConnectionField(Theme)


schema = graphene.Schema(
    query=Query,
    types=[
        Acte,
        Acteur,
        Document,
        Dossier,
        Legislature,
        Mandat,
        Organe,
        Regime,
        Theme,
    ]
)
