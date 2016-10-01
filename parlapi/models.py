# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

#
# Modeles internes
#

class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String)
    date_exec = db.Column(db.DateTime)
    url_fichier = db.Column(db.String)
    date_fichier = db.Column(db.DateTime)
    resultat = db.Column(db.String)

#
# AN: acteurs, mandats, organes
#

class Regime(db.Model):
    __tablename__ = 'regimes'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String)

    organes = db.relationship('Organe', back_populates='regime')

    legislatures = db.relationship('Legislature', back_populates='regime')


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
    db.Column('mandat_id', db.String, db.ForeignKey('mandats.id')),
    db.Column('organe_id', db.String, db.ForeignKey('organes.id'))
)


class Organe(db.Model):
    __tablename__ = 'organes'

    id = db.Column(db.String, primary_key=True)
    type = db.Column(db.String)
    libelle = db.Column(db.String)
    libelle_court = db.Column(db.String)
    abbreviation = db.Column(db.String)
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)

    regime_id = db.Column(db.Integer, db.ForeignKey('regimes.id'))
    regime = db.relationship('Regime', back_populates='organes')

    legislature_id = db.Column(db.Integer, db.ForeignKey('legislatures.id'))
    legislature = db.relationship('Legislature', back_populates='organes')

    mandats = db.relationship('Mandat', secondary=assoc_mandats_organes,
                              back_populates='organes')

    documents = db.relationship('OrganeDocument', back_populates='organe')


class Mandat(db.Model):
    __tablename__ = 'mandats'

    id = db.Column(db.String, primary_key=True)

    date_debut = db.Column(db.Date)
    date_publication = db.Column(db.Date)
    date_fin = db.Column(db.Date)

    libelle = db.Column(db.String)
    qualite = db.Column(db.String)
    preseance = db.Column(db.Integer)
    nomination_principale = db.Column(db.Boolean)

    url_hatvp = db.Column(db.String)

    election_region = db.Column(db.String)
    election_dept = db.Column(db.String)
    election_dept_num = db.Column(db.String)
    election_circo = db.Column(db.Integer)
    election_cause = db.Column(db.String)

    organes = db.relationship('Organe', secondary=assoc_mandats_organes,
                              back_populates='mandats')

    acteur_id = db.Column(db.String, db.ForeignKey('acteurs.id'))
    acteur = db.relationship('Acteur', back_populates='mandats')


class Acteur(db.Model):
    __tablename__ = 'acteurs'

    id = db.Column(db.String, primary_key=True)

    civilite = db.Column(db.String)
    nom = db.Column(db.String)
    prenom = db.Column(db.String)

    date_naissance = db.Column(db.Date)
    pays_naissance = db.Column(db.String)
    dept_naissance = db.Column(db.String)
    ville_naissance = db.Column(db.String)
    date_deces = db.Column(db.Date)

    profession = db.Column(db.String)
    profession_cat_insee = db.Column(db.String)
    profession_fam_insee = db.Column(db.String)

    mandats = db.relationship('Mandat', back_populates='acteur')

    documents = db.relationship('ActeurDocument', back_populates='acteur')

#
# AN: documents et dossiers législatifs
#


assoc_documents_themes = db.Table(
    'documents_themes',
    db.Column('document_id', db.String, db.ForeignKey('documents.id')),
    db.Column('theme_id', db.Integer, db.ForeignKey('themes.id'))
)


class Theme(db.Model):
    __tablename__ = 'themes'

    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String)

    documents = db.relationship('Document', secondary=assoc_documents_themes,
                                back_populates='themes')


class ActeurDocument(db.Model):
    __tablename__ = 'acteurs_documents'

    id = db.Column(db.Integer, primary_key=True)

    qualite = db.Column(db.String)
    relation = db.Column(db.String)

    date_cosignature = db.Column(db.Date)
    date_retrait_cosignature = db.Column(db.Date)

    acteur_id = db.Column(db.String, db.ForeignKey('acteurs.id'))
    acteur = db.relationship('Acteur', back_populates='documents')

    document_id = db.Column(db.String, db.ForeignKey('documents.id'))
    document = db.relationship('Document', back_populates='acteurs')


class OrganeDocument(db.Model):
    __tablename__ = 'organes_documents'

    id = db.Column(db.Integer, primary_key=True)

    relation = db.Column(db.String)

    date_cosignature = db.Column(db.Date)
    date_retrait_cosignature = db.Column(db.Date)

    organe_id = db.Column(db.String, db.ForeignKey('organes.id'))
    organe = db.relationship('Organe', back_populates='documents')

    document_id = db.Column(db.String, db.ForeignKey('documents.id'))
    document = db.relationship('Document', back_populates='organes')


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.String, primary_key=True)

    date_creation = db.Column(db.Date)
    date_depot = db.Column(db.Date)
    date_publication = db.Column(db.Date)
    date_publication_web = db.Column(db.Date)

    titre = db.Column(db.String)
    denomination_structurelle = db.Column(db.String)
    type_code = db.Column(db.String)
    type_libelle = db.Column(db.String)
    soustype_code = db.Column(db.String)
    soustype_libelle = db.Column(db.String)
    statut_adoption = db.Column(db.String)

    legislature_id = db.Column(db.Integer, db.ForeignKey('legislatures.id'))
    legislature = db.relationship('Legislature')

    themes = db.relationship('Theme', secondary=assoc_documents_themes,
                             back_populates='documents')

    acteurs = db.relationship('ActeurDocument', back_populates='document')

    organes = db.relationship('OrganeDocument', back_populates='document')

    document_id = db.Column(db.String, db.ForeignKey('documents.id'))
    divisions = db.relationship('Document', backref=db.backref(
                                'document_parent', remote_side=[id]))

    actes_legislatifs = db.relationship('Acte', back_populates='document')


class Dossier(db.Model):
    __tablename__ = 'dossiers'

    id = db.Column(db.String, primary_key=True)

    titre = db.Column(db.String)
    titre_chemin = db.Column(db.String)
    senat_chemin = db.Column(db.String)

    procedure_code = db.Column(db.Integer)
    procedure_libelle = db.Column(db.String)

    legislature_id = db.Column(db.Integer, db.ForeignKey('legislatures.id'))
    legislature = db.relationship('Legislature')

    # TODO initiateurs (acteurs + organes)

    actes_legislatifs = db.relationship('Acte', back_populates='dossier')


class Acte(db.Model):
    __tablename__ = 'actes'

    id = db.Column(db.String, primary_key=True)

    code = db.Column(db.String)
    libelle = db.Column(db.String)
    date = db.Column(db.Date)

    document_id = db.Column(db.String, db.ForeignKey('documents.id'))
    document = db.relationship('Document', back_populates='actes_legislatifs')

    dossier_id = db.Column(db.String, db.ForeignKey('dossiers.id'))
    dossier = db.relationship('Dossier', back_populates='actes_legislatifs')

    organe_id = db.Column(db.String, db.ForeignKey('organes.id'))
    organe = db.relationship('Organe')

    acte_id = db.Column(db.String, db.ForeignKey('actes.id'))
    actes = db.relationship('Acte', backref=db.backref('acte_parent',
                                                       remote_side=[id]))
