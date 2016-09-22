# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String)
    date_exec = db.Column(db.DateTime)
    url_fichier = db.Column(db.String)
    date_fichier = db.Column(db.DateTime)
    resultat = db.Column(db.String)


class Regime(db.Model):
    __tablename__ = 'regimes'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String)

    organes = db.relationship("Organe", back_populates="regime")

    legislatures = db.relationship("Legislature", back_populates="regime")


class Legislature(db.Model):
    __tablename__ = 'legislatures'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer)
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)

    regime_id = db.Column(db.Integer, db.ForeignKey('regimes.id'))
    regime = db.relationship("Regime", back_populates="legislatures")

    organes = db.relationship("Organe", back_populates="legislature")


assoc_mandats_organes = db.Table(
    'mandats_organes',
    db.Column('mandat_id', db.Integer, db.ForeignKey('mandats.id')),
    db.Column('organe_id', db.Integer, db.ForeignKey('organes.id'))
)


class Organe(db.Model):
    __tablename__ = 'organes'

    id = db.Column(db.Integer, primary_key=True)
    id_an = db.Column(db.String)
    type = db.Column(db.String)
    libelle = db.Column(db.String)
    libelle_court = db.Column(db.String)
    abbreviation = db.Column(db.String)
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)

    regime_id = db.Column(db.Integer, db.ForeignKey('regimes.id'))
    regime = db.relationship("Regime", back_populates="organes")

    legislature_id = db.Column(db.Integer, db.ForeignKey('legislatures.id'))
    legislature = db.relationship("Legislature", back_populates="organes")

    mandats = db.relationship("Mandat", secondary=assoc_mandats_organes,
                              back_populates="organes")


class Mandat(db.Model):
    __tablename__ = 'mandats'

    id = db.Column(db.Integer, primary_key=True)
    id_an = db.Column(db.String)

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

    organes = db.relationship("Organe", secondary=assoc_mandats_organes,
                              back_populates="mandats")

    acteur_id = db.Column(db.Integer, db.ForeignKey('acteurs.id'))
    acteur = db.relationship("Acteur", back_populates="mandats")


class Acteur(db.Model):
    __tablename__ = 'acteurs'

    id = db.Column(db.Integer, primary_key=True)
    id_an = db.Column(db.String)

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

    mandats = db.relationship("Mandat", back_populates="acteur")
