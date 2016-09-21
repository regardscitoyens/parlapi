# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


SHORT_STRING = 64
MEDIUM_STRING = 255
LARGE_STRING = 2048


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(MEDIUM_STRING))
    date_exec = db.Column(db.DateTime)
    url_fichier = db.Column(db.String(LARGE_STRING))
    date_fichier = db.Column(db.DateTime)
    resultat = db.Column(db.String(MEDIUM_STRING))


class Regime(db.Model):
    __tablename__ = 'regimes'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(MEDIUM_STRING))

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


class Organe(db.Model):
    __tablename__ = 'organes'

    id = db.Column(db.Integer, primary_key=True)
    id_an = db.Column(db.String(SHORT_STRING))
    type = db.Column(db.String(SHORT_STRING))
    libelle = db.Column(db.String(LARGE_STRING))
    libelle_court = db.Column(db.String(MEDIUM_STRING))
    abbreviation = db.Column(db.String(SHORT_STRING))
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)

    regime_id = db.Column(db.Integer, db.ForeignKey('regimes.id'))
    regime = db.relationship("Regime", back_populates="organes")

    legislature_id = db.Column(db.Integer, db.ForeignKey('legislatures.id'))
    legislature = db.relationship("Legislature", back_populates="organes")

    mandats = db.relationship("Mandat", back_populates="organe")


class Acteur(db.Model):
    __tablename__ = 'acteurs'

    id = db.Column(db.Integer, primary_key=True)
    id_an = db.Column(db.String(SHORT_STRING))

    civilite = db.Column(db.String(SHORT_STRING))
    nom = db.Column(db.String(MEDIUM_STRING))
    prenom = db.Column(db.String(MEDIUM_STRING))

    date_naissance = db.Column(db.Date)
    pays_naissance = db.Column(db.String(MEDIUM_STRING))
    dept_naissance = db.Column(db.String(MEDIUM_STRING))
    ville_naissance = db.Column(db.String(MEDIUM_STRING))
    date_deces = db.Column(db.Date)

    profession = db.Column(db.String(MEDIUM_STRING))
    profession_cat_insee = db.Column(db.String(MEDIUM_STRING))
    profession_fam_insee = db.Column(db.String(MEDIUM_STRING))

    mandats = db.relationship("Mandat", back_populates="acteur")


class Mandat(db.Model):
    __tablename__ = 'mandats'

    id = db.Column(db.Integer, primary_key=True)
    id_an = db.Column(db.String(SHORT_STRING))

    date_debut = db.Column(db.Date)
    date_publication = db.Column(db.Date)
    date_fin = db.Column(db.Date)

    libelle = db.Column(db.String(LARGE_STRING))
    qualite = db.Column(db.String(MEDIUM_STRING))
    preseance = db.Column(db.Integer)
    nomination_principale = db.Column(db.Boolean)

    url_hatvp = db.Column(db.String(LARGE_STRING))

    election_region = db.Column(db.String(MEDIUM_STRING))
    election_dept = db.Column(db.String(MEDIUM_STRING))
    election_dept_num = db.Column(db.String(SHORT_STRING))
    election_circo = db.Column(db.Integer)
    election_cause = db.Column(db.String(MEDIUM_STRING))

    organe_id = db.Column(db.Integer, db.ForeignKey('organes.id'))
    organe = db.relationship("Organe", back_populates="mandats")

    acteur_id = db.Column(db.Integer, db.ForeignKey('acteurs.id'))
    acteur = db.relationship("Acteur", back_populates="mandats")
