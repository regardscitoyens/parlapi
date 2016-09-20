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


class Legislature(db.Model):
    __tablename__ = 'legislatures'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer)
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)

    regime_id = db.Column(db.Integer, db.ForeignKey('regimes.id'))
    regime = db.relationship("Regime", back_populates="legislatures")


Regime.legislatures = db.relationship("Legislature", order_by=Legislature.id,
                                      back_populates="regime")


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


Regime.organes = db.relationship("Organe", order_by=Organe.id,
                                 back_populates="regime")
Legislature.organes = db.relationship("Organe", order_by=Organe.id,
                                      back_populates="legislature")


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
