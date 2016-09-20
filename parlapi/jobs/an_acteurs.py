# -*- coding: utf-8 -*-

import dateparser
import ijson

from .base import BaseANJob
from ..models import Acteur


class ImportActeursJob(BaseANJob):

    @property
    def job_name(self):
        return u'Import acteurs AN'

    def __init__(self, app):
        super(ImportActeursJob, self).__init__(
            app, '/acteurs/deputes-en-exercice')

    def parse_json(self, filename, stream):
        for acteur_json in ijson.items(stream, 'export.acteurs.acteur.item'):
            self.save_acteur(acteur_json)

    def save_acteur(self, json):
        acteur = self.get_or_create(Acteur, id_an=json['uid']['#text'])

        ec = json['etatCivil']
        id = ec['ident']

        acteur.civilite = id['civ']
        acteur.nom = id['nom']
        acteur.prenom = id['prenom']

        nais = ec['infoNaissance']

        acteur.date_naissance = dateparser.parse(nais['dateNais'])
        acteur.ville_naissance = nais['villeNais']
        acteur.dept_naissance = nais['depNais']
        acteur.pays_naissance = nais['paysNais']

        if ec.get('dateDeces', None):
            acteur.date_deces = dateparser.parse(ec['dateDeces'])

        pro = json['profession']

        acteur.profession = pro['libelleCourant']
        acteur.profession_cat_insee = pro['socProcINSEE']['catSocPro']
        acteur.profession_fam_insee = pro['socProcINSEE']['famSocPro']


def run(app, force):
    ImportActeursJob(app).run(force)
