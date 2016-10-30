# -*- coding: utf-8 -*-

from flask_marshmallow import Marshmallow
from sqlalchemy.orm import joinedload

from .api import API
from .utils import prefetched
from ..models import (
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
    Votant
)


def setup_api(app):
    ma = Marshmallow(app)
    api = API(ma, app)

    class ParlapiBaseMeta:
        exclude = ('search_vector',)

    # Base schemas (for use in lists & some relations)

    class JobSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = Job
            fields = ()

    class RegimeBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = Regime
            fields = ('nom', '_url')

        _url = api.detailURL('regimes')

    class LegislatureBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = Legislature
            fields = ('id', '_url')

        _url = api.detailURL('legislatures')

    class OrganeBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = Organe
            fields = ('libelle', 'type', '_url')

        _url = api.detailURL('organes')

    class ActeurBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = Acteur
            fields = ('nom', 'prenom', '_url')

        _url = api.detailURL('acteurs')

    class MandatBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = Mandat
            fields = ('qualite', '_url')

        _url = api.detailURL('mandats')

    class ThemeBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = Theme
            fields = ('theme', '_url')

        _url = api.detailURL('themes')

    class ActeurDocumentBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = ActeurDocument
            fields = ('date_cosignature', 'date_retrait_cosignature',
                      'qualite', 'relation')

    class ActeurDossierBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = ActeurDossier
            fields = ('relation',)

    class OrganeDocumentBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = OrganeDocument
            fields = ('date_cosignature', 'date_retrait_cosignature',
                      'relation')

    class OrganeDossierBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = OrganeDossier
            fields = ('relation',)

    class DocumentBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = Document
            fields = ('denomination_structurelle', 'titre', '_url')

        _url = api.detailURL('documents')

    class DossierBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = Dossier
            fields = ('titre', 'procedure_libelle', '_url')

        _url = api.detailURL('dossiers')

    class ActeBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = Acte
            fields = ('libelle', '_url')

        _url = api.detailURL('actes')

    class AmendementBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = Amendement
            fields = ('numero_long', 'etape_texte', 'sort', 'division_texte',
                      '_url')

        _url = api.detailURL('amendements')

    class ScrutinBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = Scrutin
            fields = ('titre', 'date', 'sort_code', '_url')

        _url = api.detailURL('scrutins')

    class ODJItemBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = ODJItem
            fields = ('item',)

    class ODJPointBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = ODJPoint
            fields = ('objet', 'dossiers')

        dossiers = api.nestedList(DossierBaseSchema)

    class ReunionBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = Reunion
            fields = ('type_reunion', 'date_debut', 'date_fin', 'lieu_libelle',
                      '_url', 'items_odj', 'points_odj')

        items_odj = api.nestedList(ODJItemBaseSchema)
        points_odj = api.nestedList(ODJPointBaseSchema)
        _url = api.detailURL('reunions')

    class ActeurReunionBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = ActeurReunion
            fields = ('relation', 'presence')

    class OrganeReunionBaseSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = OrganeReunion
            fields = ('relation',)

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

    class ActeurDocumentDocumentSchema(ActeurDocumentBaseSchema):
        class Meta(ActeurDocumentBaseSchema.Meta):
            fields = ActeurDocumentBaseSchema.Meta.fields + ('acteur',)

        acteur = api.nested(ActeurBaseSchema)

    class ActeurDossierDossierSchema(ActeurDossierBaseSchema):
        class Meta(ActeurDossierBaseSchema.Meta):
            fields = ActeurDossierBaseSchema.Meta.fields + ('acteur', 'mandat')

        acteur = api.nested(ActeurBaseSchema)
        mandat = api.nested(MandatActeurSchema)

    class OrganeDocumentDocumentSchema(OrganeDocumentBaseSchema):
        class Meta(OrganeDocumentBaseSchema.Meta):
            fields = OrganeDocumentBaseSchema.Meta.fields + ('organe',)

        organe = api.nested(OrganeBaseSchema)

    class OrganeDossierDossierSchema(OrganeDossierBaseSchema):
        class Meta(OrganeDossierBaseSchema.Meta):
            fields = OrganeDossierBaseSchema.Meta.fields + ('organe',)

        organe = api.nested(OrganeBaseSchema)

    class AmendementListSchema(AmendementBaseSchema):
        class Meta(AmendementBaseSchema.Meta):
            fields = AmendementBaseSchema.Meta.fields + ('document',)

        document = api.nested(DocumentBaseSchema)

    class ActeurReunionReunionSchema(ActeurReunionBaseSchema):
        class Meta(ActeurReunionBaseSchema.Meta):
            fields = ActeurReunionBaseSchema.Meta.fields + ('acteur',)

        acteur = api.nested(ActeurBaseSchema)

    class OrganeReunionReunionSchema(OrganeReunionBaseSchema):
        class Meta(OrganeReunionBaseSchema.Meta):
            fields = OrganeReunionBaseSchema.Meta.fields + ('organe',)

        organe = api.nested(OrganeBaseSchema)

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

        actes_legislatifs = api.nestedList(ActeBaseSchema)
        acteurs = api.nestedList(ActeurDocumentDocumentSchema)
        amendements = api.nestedList(AmendementBaseSchema)
        document_parent = api.nested(DocumentBaseSchema)
        dossier = api.nested(DossierBaseSchema)
        divisions = api.nestedList(DocumentBaseSchema)
        legislature = api.nested(LegislatureBaseSchema)
        organes = api.nestedList(OrganeDocumentDocumentSchema)
        themes = api.nestedList(ThemeBaseSchema)

    class DossierDetailSchema(DossierBaseSchema):
        class Meta(DossierBaseSchema.Meta):
            fields = ()

        actes_legislatifs = api.nestedList(ActeBaseSchema)
        acteurs = api.nestedList(ActeurDossierDossierSchema)
        documents = api.nestedList(DocumentBaseSchema)
        legislature = api.nested(LegislatureBaseSchema)
        organes = api.nestedList(OrganeDossierDossierSchema)

    class ActeDetailSchema(ActeBaseSchema):
        class Meta(ActeBaseSchema.Meta):
            fields = ()

        acte_parent = api.nested(ActeBaseSchema)
        actes = api.nestedList(ActeBaseSchema)
        document = api.nested(DocumentBaseSchema)
        dossier = api.nested(DossierBaseSchema)
        organe = api.nested(OrganeBaseSchema)

    class AmendementDetailSchema(AmendementBaseSchema):
        class Meta(AmendementBaseSchema.Meta):
            fields = ()

        amendement_parent = api.nested(AmendementBaseSchema)
        document = api.nested(DocumentBaseSchema)
        legislature = api.nested(LegislatureBaseSchema)
        organe = api.nested(OrganeBaseSchema)
        sous_amendements = api.nestedList(AmendementBaseSchema)

    class VotantSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = Votant
            exclude = ('groupe', 'id', 'mandat')

        acteur = api.nested(ActeurBaseSchema)

    class ScrutinGroupeSchema(ma.ModelSchema):
        class Meta(ParlapiBaseMeta):
            model = ScrutinGroupe
            exclude = ('scrutin', 'id')

        organe = api.nested(OrganeBaseSchema)
        votants = api.nestedList(VotantSchema)

    class ScrutinDetailSchema(ScrutinBaseSchema):
        class Meta(ScrutinBaseSchema.Meta):
            fields = ()

        legislature = api.nested(LegislatureBaseSchema)
        organe = api.nested(OrganeBaseSchema)
        groupes = api.nestedList(ScrutinGroupeSchema)

    class ODJPointReunionSchema(ODJPointBaseSchema):
        class Meta(ODJPointBaseSchema.Meta):
            fields = ()
            exclude = ('reunion', 'id', 'search_vector')

    class ReunionDetailSchema(ReunionBaseSchema):
        class Meta(ReunionBaseSchema.Meta):
            fields = ()

        points_odj = api.nestedList(ODJPointReunionSchema)
        organes = api.nestedList(OrganeReunionReunionSchema)
        acteurs = api.nestedList(ActeurReunionReunionSchema)

    # API creation

    api.endpoint(
        Job,
        JobSchema,
        description=u'Jobs d\'import de données'
    )

    api.endpoint(
        Regime,
        RegimeDetailSchema,
        list_schema=RegimeBaseSchema,
        description=u'Régimes politiques',
        detail_query=prefetched(Regime, ['organes', 'legislatures'])
    )

    api.endpoint(
        Legislature,
        LegislatureDetailSchema,
        list_schema=LegislatureBaseSchema,
        description=u'Législatures',
        detail_query=prefetched(Legislature, ['organes', 'regime'])
    )

    api.endpoint(
        Organe,
        OrganeDetailSchema,
        list_schema=OrganeBaseSchema,
        description=u'Organes (ministères, commissions, organismes...)',
        detail_query=prefetched(Organe, ['legislature', 'regime',
                                         'mandats.acteur'])
    )

    api.endpoint(
        Acteur,
        ActeurDetailSchema,
        list_schema=ActeurBaseSchema,
        description=u'Acteurs (ministres, parlementaires...)',
        detail_query=prefetched(Acteur, ['mandats.organes'])
    )

    api.endpoint(
        Mandat,
        MandatDetailSchema,
        list_schema=MandatListSchema,
        description=u'Mandats',
        query=prefetched(Mandat, ['organes', 'acteur'])
    )

    api.endpoint(
        Theme,
        ThemeDetailSchema,
        list_schema=ThemeBaseSchema,
        description=u'Thèmes',
        detail_query=prefetched(Theme, ['documents'])
    )

    api.endpoint(
        Document,
        DocumentDetailSchema,
        list_schema=DocumentBaseSchema,
        description=u'Documents législatifs',
        detail_query=prefetched(Document, ['actes_legislatifs',
                                           'acteurs.acteur', 'document_parent',
                                           'dossier', 'divisions',
                                           'legislature', 'organes.organe',
                                           'themes'])
    )

    api.endpoint(
        Dossier,
        DossierDetailSchema,
        list_schema=DossierBaseSchema,
        description=u'Dossiers législatifs',
        detail_query=prefetched(Dossier, ['actes_legislatifs',
                                          'acteurs.acteur',
                                          'acteurs.mandat.organes',
                                          'documents',
                                          'organes.organe',
                                          'legislature'])
    )

    api.endpoint(
        Acte,
        ActeDetailSchema,
        list_schema=ActeBaseSchema,
        description=u'Actes législatifs',
        detail_query=prefetched(Acte, ['acte_parent', 'actes', 'organe'])
    )

    api.endpoint(
        Amendement,
        AmendementDetailSchema,
        list_schema=AmendementListSchema,
        description=u'Amendements',
        detail_query=prefetched(Amendement, ['legislature', 'document',
                                             'organe', 'sous_amendements',
                                             'amendement_parent'])
    )

    api.endpoint(
        Scrutin,
        ScrutinDetailSchema,
        list_schema=ScrutinBaseSchema,
        description=u'Scrutins',
        detail_query=prefetched(Scrutin, ['legislature', 'organe',
                                          'groupes.organe',
                                          'gropes.votants.acteur'])
    )

    api.endpoint(
        Reunion,
        ReunionDetailSchema,
        list_schema=ReunionBaseSchema,
        description=u'Réunions',
        list_query=prefetched(Reunion, ['items_odj', 'points_odj.dossiers']),
        detail_query=prefetched(Reunion, ['items_odj', 'points_odj.dossiers',
                                          'organes.organe', 'acteurs.acteur'])
    )

    return api
