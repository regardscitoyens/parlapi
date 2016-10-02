# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy_searchable import make_searchable, SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType


db = SQLAlchemy()
make_searchable(options={'regconfig': 'pg_catalog.french'})


class SearchableQuery(BaseQuery, SearchQueryMixin):
    pass


#
# Modeles internes
#

class Job(db.Model):
    __tablename__ = 'jobs'
    query_class = SearchableQuery

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.Unicode)
    date_exec = db.Column(db.DateTime)
    url_fichier = db.Column(db.Unicode)
    date_fichier = db.Column(db.DateTime)
    resultat = db.Column(db.Unicode)

    search_vector = db.Column(TSVectorType('nom', 'url_fichier'))


#
# AN: acteurs, mandats, organes
#

class Regime(db.Model):
    __tablename__ = 'regimes'
    query_class = SearchableQuery

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.Unicode)

    organes = db.relationship('Organe', back_populates='regime')

    legislatures = db.relationship('Legislature', back_populates='regime')

    search_vector = db.Column(TSVectorType('nom'))


class Legislature(db.Model):
    __tablename__ = 'legislatures'

    id = db.Column(db.Integer, primary_key=True)
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)

    regime_id = db.Column(db.Integer, db.ForeignKey('regimes.id'))
    regime = db.relationship('Regime', back_populates='legislatures')

    organes = db.relationship('Organe', back_populates='legislature')


assoc_mandats_organes = db.Table(
    'mandats_organes',
    db.Column('mandat_id', db.Unicode, db.ForeignKey('mandats.id')),
    db.Column('organe_id', db.Unicode, db.ForeignKey('organes.id'))
)


class Organe(db.Model):
    __tablename__ = 'organes'
    query_class = SearchableQuery

    id = db.Column(db.Unicode, primary_key=True)
    type = db.Column(db.Unicode)
    libelle = db.Column(db.Unicode)
    libelle_court = db.Column(db.Unicode)
    abbreviation = db.Column(db.Unicode)
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)

    regime_id = db.Column(db.Integer, db.ForeignKey('regimes.id'))
    regime = db.relationship('Regime', back_populates='organes')

    legislature_id = db.Column(db.Integer, db.ForeignKey('legislatures.id'))
    legislature = db.relationship('Legislature', back_populates='organes')

    mandats = db.relationship('Mandat', secondary=assoc_mandats_organes,
                              back_populates='organes')

    documents = db.relationship('OrganeDocument', back_populates='organe')

    search_vector = db.Column(TSVectorType('libelle', 'libelle_court', 'type',
                                           'abbreviation'))


class Mandat(db.Model):
    __tablename__ = 'mandats'
    query_class = SearchableQuery

    id = db.Column(db.Unicode, primary_key=True)

    date_debut = db.Column(db.Date)
    date_publication = db.Column(db.Date)
    date_fin = db.Column(db.Date)

    libelle = db.Column(db.Unicode)
    qualite = db.Column(db.Unicode)
    preseance = db.Column(db.Integer)
    nomination_principale = db.Column(db.Boolean)

    url_hatvp = db.Column(db.Unicode)

    election_region = db.Column(db.Unicode)
    election_dept = db.Column(db.Unicode)
    election_dept_num = db.Column(db.Unicode)
    election_circo = db.Column(db.Integer)
    election_cause = db.Column(db.Unicode)

    organes = db.relationship('Organe', secondary=assoc_mandats_organes,
                              back_populates='mandats')

    acteur_id = db.Column(db.Unicode, db.ForeignKey('acteurs.id'))
    acteur = db.relationship('Acteur', back_populates='mandats')

    search_vector = db.Column(TSVectorType('libelle', 'qualite',
                                           'election_region', 'election_dept',
                                           'election_dept_num',
                                           'election_cause'))


class Acteur(db.Model):
    __tablename__ = 'acteurs'
    query_class = SearchableQuery

    id = db.Column(db.Unicode, primary_key=True)

    civilite = db.Column(db.Unicode)
    nom = db.Column(db.Unicode)
    prenom = db.Column(db.Unicode)

    date_naissance = db.Column(db.Date)
    pays_naissance = db.Column(db.Unicode)
    dept_naissance = db.Column(db.Unicode)
    ville_naissance = db.Column(db.Unicode)
    date_deces = db.Column(db.Date)

    profession = db.Column(db.Unicode)
    profession_cat_insee = db.Column(db.Unicode)
    profession_fam_insee = db.Column(db.Unicode)

    mandats = db.relationship('Mandat', back_populates='acteur')

    documents = db.relationship('ActeurDocument', back_populates='acteur')

    search_vector = db.Column(TSVectorType('civilite', 'nom', 'prenom',
                                           'profession'))

#
# AN: documents et dossiers législatifs
#


assoc_documents_themes = db.Table(
    'documents_themes',
    db.Column('document_id', db.Unicode, db.ForeignKey('documents.id')),
    db.Column('theme_id', db.Integer, db.ForeignKey('themes.id'))
)


class Theme(db.Model):
    __tablename__ = 'themes'
    query_class = SearchableQuery

    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.Unicode)

    documents = db.relationship('Document', secondary=assoc_documents_themes,
                                back_populates='themes')

    search_vector = db.Column(TSVectorType('theme'))


class ActeurDocument(db.Model):
    __tablename__ = 'acteurs_documents'
    query_class = SearchableQuery

    id = db.Column(db.Integer, primary_key=True)

    qualite = db.Column(db.Unicode)
    relation = db.Column(db.Unicode)

    date_cosignature = db.Column(db.Date)
    date_retrait_cosignature = db.Column(db.Date)

    acteur_id = db.Column(db.Unicode, db.ForeignKey('acteurs.id'))
    acteur = db.relationship('Acteur', back_populates='documents')

    document_id = db.Column(db.Unicode, db.ForeignKey('documents.id'))
    document = db.relationship('Document', back_populates='acteurs')


class OrganeDocument(db.Model):
    __tablename__ = 'organes_documents'
    query_class = SearchableQuery

    id = db.Column(db.Integer, primary_key=True)

    relation = db.Column(db.Unicode)

    date_cosignature = db.Column(db.Date)
    date_retrait_cosignature = db.Column(db.Date)

    organe_id = db.Column(db.Unicode, db.ForeignKey('organes.id'))
    organe = db.relationship('Organe', back_populates='documents')

    document_id = db.Column(db.Unicode, db.ForeignKey('documents.id'))
    document = db.relationship('Document', back_populates='organes')


class Document(db.Model):
    __tablename__ = 'documents'
    query_class = SearchableQuery

    id = db.Column(db.Unicode, primary_key=True)

    date_creation = db.Column(db.Date)
    date_depot = db.Column(db.Date)
    date_publication = db.Column(db.Date)
    date_publication_web = db.Column(db.Date)

    titre = db.Column(db.Unicode)
    denomination_structurelle = db.Column(db.Unicode)
    type_code = db.Column(db.Unicode)
    type_libelle = db.Column(db.Unicode)
    soustype_code = db.Column(db.Unicode)
    soustype_libelle = db.Column(db.Unicode)
    statut_adoption = db.Column(db.Unicode)

    legislature_id = db.Column(db.Integer, db.ForeignKey('legislatures.id'))
    legislature = db.relationship('Legislature')

    themes = db.relationship('Theme', secondary=assoc_documents_themes,
                             back_populates='documents')

    acteurs = db.relationship('ActeurDocument', back_populates='document')

    organes = db.relationship('OrganeDocument', back_populates='document')

    document_id = db.Column(db.Unicode, db.ForeignKey('documents.id'))
    divisions = db.relationship('Document', backref=db.backref(
                                'document_parent', remote_side=[id]))

    actes_legislatifs = db.relationship('Acte', back_populates='document')

    amendements = db.relationship('Amendement', back_populates='document')

    dossier_id = db.Column(db.Unicode, db.ForeignKey('dossiers.id'))
    dossier = db.relationship('Dossier', back_populates='documents')

    search_vector = db.Column(TSVectorType('titre', 'type_code',
                                           'type_libelle', 'soustype_code',
                                           'soustype_libelle',
                                           'statut_adoption',
                                           'denomination_structurelle'))


class Dossier(db.Model):
    __tablename__ = 'dossiers'
    query_class = SearchableQuery

    id = db.Column(db.Unicode, primary_key=True)

    titre = db.Column(db.Unicode)
    titre_chemin = db.Column(db.Unicode)
    senat_chemin = db.Column(db.Unicode)

    procedure_code = db.Column(db.Integer)
    procedure_libelle = db.Column(db.Unicode)

    legislature_id = db.Column(db.Integer, db.ForeignKey('legislatures.id'))
    legislature = db.relationship('Legislature')

    # TODO initiateurs (acteurs + organes)

    actes_legislatifs = db.relationship('Acte', back_populates='dossier')

    documents = db.relationship('Document', back_populates='dossier')

    search_vector = db.Column(TSVectorType('titre', 'procedure_libelle',
                                           'senat_chemin', 'titre_chemin'))


class Acte(db.Model):
    __tablename__ = 'actes'
    query_class = SearchableQuery

    id = db.Column(db.Unicode, primary_key=True)

    code = db.Column(db.Unicode)
    libelle = db.Column(db.Unicode)
    date = db.Column(db.Date)

    document_id = db.Column(db.Unicode, db.ForeignKey('documents.id'))
    document = db.relationship('Document', back_populates='actes_legislatifs')

    dossier_id = db.Column(db.Unicode, db.ForeignKey('dossiers.id'))
    dossier = db.relationship('Dossier', back_populates='actes_legislatifs')

    organe_id = db.Column(db.Unicode, db.ForeignKey('organes.id'))
    organe = db.relationship('Organe')

    acte_id = db.Column(db.Unicode, db.ForeignKey('actes.id'))
    actes = db.relationship('Acte', backref=db.backref('acte_parent',
                                                       remote_side=[id]))

    search_vector = db.Column(TSVectorType('code', 'libelle'))


class Amendement(db.Model):
    __tablename__ = 'amendements'
    query_class = SearchableQuery

    id = db.Column(db.Unicode, primary_key=True)

    numero = db.Column(db.Integer)
    num_rect = db.Column(db.Integer)
    numero_long = db.Column(db.Unicode)
    etape_texte = db.Column(db.Unicode)
    tri = db.Column(db.Unicode)
    cardinal_multiples = db.Column(db.Integer)
    etat = db.Column(db.Unicode)
    article_99 = db.Column(db.Boolean)
    sort = db.Column(db.Unicode)
    date_sort = db.Column(db.Date)

    division_texte = db.Column(db.Unicode)
    division_position = db.Column(db.Unicode)
    division_article_additionnel = db.Column(db.Boolean)
    division_chapitre_additionnel = db.Column(db.Boolean)
    division_alinea = db.Column(db.Integer)
    division_alinea_position = db.Column(db.Unicode)

    corps_dispositif = db.Column(db.UnicodeText)
    corps_expose = db.Column(db.UnicodeText)

    code_loi = db.Column(db.Unicode)
    code_loi_division = db.Column(db.Unicode)

    date_depot = db.Column(db.Date)
    date_distribution = db.Column(db.Date)

    # TODO référence séance json['seanceDiscussion']
    # TODO auteurs/cosignataires

    legislature_id = db.Column(db.Integer, db.ForeignKey('legislatures.id'))
    legislature = db.relationship('Legislature')

    document_id = db.Column(db.Unicode, db.ForeignKey('documents.id'))
    document = db.relationship('Document', back_populates='amendements')

    organe_id = db.Column(db.Unicode, db.ForeignKey('organes.id'))
    organe = db.relationship('Organe')

    amendement_id = db.Column(db.Unicode, db.ForeignKey('amendements.id'))
    sous_amendements = db.relationship('Amendement',
                                       backref=db.backref('amendement_parent',
                                                          remote_side=[id]))

    search_vector = db.Column(TSVectorType('numero_long', 'corps_expose',
                                           'corps_dispositif', 'code_loi',
                                           'code_loi_division'))
