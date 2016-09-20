# -*- coding: utf-8 -*-

import dateparser
import ijson

from .base import BaseANJob
from ..models import Organe, Legislature, Regime


class ImportOrganesJob(BaseANJob):
    cache_legislatures = {}
    cache_regimes = {}

    @property
    def job_name(self):
        return u'Import organes AN'

    def __init__(self, app):
        super(ImportOrganesJob, self).__init__(
            app, '/acteurs/deputes-en-exercice')

    def parse_json(self, filename, stream):
        for organe_json in ijson.items(stream, 'export.organes.organe.item'):
            self.save_organe(organe_json)

    def get_regime(self, nom):
        if nom not in self.cache_regimes:
            self.cache_regimes[nom] = self.get_or_create(Regime, nom=nom)

        return self.cache_regimes[nom]

    def get_legislature(self, num):
        if num not in self.cache_legislatures:
            self.cache_legislatures[num] = self.get_or_create(Legislature,
                                                              numero=int(num))

        return self.cache_legislatures[num]

    def save_organe(self, json):
        organe = self.get_or_create(Organe, id_an=json['uid'])

        organe.type = json['codeType']
        organe.libelle = json['libelle']
        organe.libelle_court = json['libelleAbrege']
        organe.abbreviation = json['libelleAbrev']

        if json['viMoDe']['dateDebut']:
            organe.date_debut = dateparser.parse(json['viMoDe']['dateDebut'])
        else:
            organe.date_debut = None

        if json['viMoDe']['dateFin']:
            organe.date_fin = dateparser.parse(json['viMoDe']['dateFin'])
        else:
            organe.date_fin = None

        if json.get('regime', None):
            organe.regime = self.get_regime(json['regime'])

        if json.get('legislature', None):
            organe.legislature = self.get_legislature(json['legislature'])
            if organe.regime:
                organe.legislature.regime = organe.regime


def run(app, force):
    ImportOrganesJob(app).run(force)
