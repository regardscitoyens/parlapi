# -*- coding: utf-8 -*-

import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from ..models import (
    Acte as ActeModel,
    Acteur as ActeurModel,
    ActeurDocument as ActeurDocumentModel,
    ActeurDossier as ActeurDossierModel,
    ActeurReunion as ActeurReunionModel,
    Amendement as AmendementModel,
    Document as DocumentModel,
    Dossier as DossierModel,
    Job as JobModel,
    Legislature as LegislatureModel,
    Mandat as MandatModel,
    ODJItem as ODJItemModel,
    ODJPoint as ODJPointModel,
    Organe as OrganeModel,
    OrganeDocument as OrganeDocumentModel,
    OrganeDossier as OrganeDossierModel,
    OrganeReunion as OrganeReunionModel,
    Regime as RegimeModel,
    Reunion as ReunionModel,
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


class ActeurReunion(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = ActeurReunionModel


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


class ODJItem(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = ODJItemModel


class ODJPoint(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = ODJPointModel


class Organe(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = OrganeModel


class OrganeDocument(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = OrganeDocumentModel


class OrganeDossier(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = OrganeDossierModel


class OrganeReunion(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = OrganeReunionModel


class Regime(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = RegimeModel


class Reunion(SQLAlchemyObjectType):
    class Meta(ParlapiBaseMeta):
        model = ReunionModel


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
    all_reunions = SQLAlchemyConnectionField(Reunion)
    all_scrutins = SQLAlchemyConnectionField(Scrutin)
    all_themes = SQLAlchemyConnectionField(Theme)


schema = graphene.Schema(
    query=Query,
    types=[
        Acte,
        Acteur,
        ActeurDocument,
        ActeurDossier,
        ActeurReunion,
        Amendement,
        Document,
        Dossier,
        Job,
        Legislature,
        Mandat,
        ODJItem,
        ODJPoint,
        Organe,
        OrganeDocument,
        OrganeDossier,
        OrganeReunion,
        Regime,
        Reunion,
        Scrutin,
        ScrutinGroupe,
        Theme,
        Votant,
    ]
)
