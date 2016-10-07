# -*- coding: utf-8 -*-

import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from ..models import (
    Acte as ActeModel,
    Acteur as ActeurModel,
    ActeurDocument as ActeurDocumentModel,
    ActeurDossier as ActeurDossierModel,
    Amendement as AmendementModel,
    Document as DocumentModel,
    Dossier as DossierModel,
    Job as JobModel,
    Legislature as LegislatureModel,
    Mandat as MandatModel,
    Organe as OrganeModel,
    OrganeDocument as OrganeDocumentModel,
    OrganeDossier as OrganeDossierModel,
    Regime as RegimeModel,
    Scrutin as ScrutinModel,
    ScrutinGroupe as ScrutinGroupeModel,
    Theme as ThemeModel,
    Votant as VotantModel,
)


class ParlapiBaseMeta:
    exclude_fields = ('search_vector',)
    interfaces = (relay.Node,)


class Acte(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = ActeModel


class Acteur(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = ActeurModel


class ActeurDocument(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = ActeurDocumentModel


class ActeurDossier(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = ActeurDossierModel


class Amendement(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = AmendementModel


class Document(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = DocumentModel


class Dossier(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = DossierModel


class Job(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = JobModel


class Legislature(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = LegislatureModel


class Mandat(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = MandatModel


class Organe(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = OrganeModel


class OrganeDocument(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = OrganeDocumentModel


class OrganeDossier(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = OrganeDossierModel


class Regime(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = RegimeModel


class Scrutin(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = ScrutinModel


class ScrutinGroupe(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = ScrutinGroupeModel


class Theme(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = ThemeModel


class Votant(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = VotantModel


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    all_actes = SQLAlchemyConnectionField(Acte)
    all_acteurs = SQLAlchemyConnectionField(Acteur)
    all_amendements = SQLAlchemyConnectionField(Amendement)
    all_documents = SQLAlchemyConnectionField(Document)
    all_dossiers = SQLAlchemyConnectionField(Dossier)
    all_jobs = SQLAlchemyConnectionField(Job)
    all_legislatures = SQLAlchemyConnectionField(Legislature)
    all_mandats = SQLAlchemyConnectionField(Mandat)
    all_organes = SQLAlchemyConnectionField(Organe)
    all_regimes = SQLAlchemyConnectionField(Regime)
    all_scrutins = SQLAlchemyConnectionField(Scrutin)
    all_themes = SQLAlchemyConnectionField(Theme)


schema = graphene.Schema(
    query=Query,
    types=[
        Acte,
        Acteur,
        ActeurDocument,
        ActeurDossier,
        Amendement,
        Document,
        Dossier,
        Job,
        Legislature,
        Mandat,
        Organe,
        OrganeDocument,
        OrganeDossier,
        Regime,
        Scrutin,
        ScrutinGroupe,
        Theme,
        Votant,
    ]
)
