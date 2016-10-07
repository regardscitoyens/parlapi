# -*- coding: utf-8 -*-

from flask_marshmallow import Marshmallow
from sqlalchemy.orm import joinedload

from .api import API
from ..models import (
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

    # API creation

    api.endpoint(
        Job,
        JobSchema,
        description=u'Jobs d\'import de données'
    )

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

    def document_detail_query(id):
        return Document.query \
            .options(joinedload('actes_legislatifs')) \
            .options(joinedload('acteurs').joinedload('acteur')) \
            .options(joinedload('document_parent')) \
            .options(joinedload('dossier')) \
            .options(joinedload('divisions')) \
            .options(joinedload('legislature')) \
            .options(joinedload('organes').joinedload('organe')) \
            .options(joinedload('themes')) \
            .filter_by(id=id)

    api.endpoint(
        Document,
        DocumentDetailSchema,
        list_schema=DocumentBaseSchema,
        description=u'Documents législatifs',
        detail_query=document_detail_query
    )

    def dossier_detail_query(id):
        return Dossier.query \
            .options(joinedload('actes_legislatifs')) \
            .options(joinedload('acteurs').joinedload('acteur')) \
            .options(joinedload('acteurs').joinedload('mandat')
                                          .joinedload('organes')) \
            .options(joinedload('documents')) \
            .options(joinedload('organes').joinedload('organe')) \
            .options(joinedload('legislature')) \
            .filter_by(id=id)

    api.endpoint(
        Dossier,
        DossierDetailSchema,
        list_schema=DossierBaseSchema,
        description=u'Dossiers législatifs',
        detail_query=dossier_detail_query
    )

    def acte_detail_query(id):
        return Acte.query \
            .options(joinedload('acte_parent')) \
            .options(joinedload('actes')) \
            .options(joinedload('organe')) \
            .filter_by(id=id)

    api.endpoint(
        Acte,
        ActeDetailSchema,
        list_schema=ActeBaseSchema,
        description=u'Actes législatifs',
        detail_query=acte_detail_query
    )

    def amendement_detail_query(id):
        return Amendement.query \
            .options(joinedload('legislature')) \
            .options(joinedload('document')) \
            .options(joinedload('organe')) \
            .options(joinedload('sous_amendements')) \
            .options(joinedload('amendement_parent')) \
            .filter_by(id=id)

    api.endpoint(
        Amendement,
        AmendementDetailSchema,
        list_schema=AmendementListSchema,
        description=u'Amendements',
        detail_query=amendement_detail_query
    )

    def scrutin_detail_query(id):
        return Scrutin.query \
               .options(joinedload('legislature')) \
               .options(joinedload('organe')) \
               .options(joinedload('groupes').joinedload('organe')) \
               .options(joinedload('groupes').joinedload('votants').joinedload('acteur')) \
               .filter_by(id=id)

    api.endpoint(
        Scrutin,
        ScrutinDetailSchema,
        list_schema=ScrutinBaseSchema,
        description=u'Scrutins',
        detail_query=scrutin_detail_query
    )

    return api
