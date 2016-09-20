# -*- coding: utf-8 -*-

import dateparser
import ijson

from .base import BaseANJob
from ..models import Organe, Acteur, Mandat


class ImportActeursJob(BaseANJob):
    cache_organes = {}

    @property
    def job_name(self):
        return u'Import acteurs AN'

    def __init__(self, app):
        super(ImportActeursJob, self).__init__(
            app, '/acteurs/deputes-en-exercice')

    def parse_json(self, filename, stream):
        for acteur_json in ijson.items(stream, 'export.acteurs.acteur.item'):
            self.save_acteur(acteur_json)

    def get_organe(self, id_an):
        if id_an not in self.cache_organes:
            self.cache_organes[id_an] = self.get_or_create(Organe, id_an=id_an)

        return self.cache_organes[id_an]

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

        for mandat_json in json['mandats']['mandat']:
            self.save_mandat(acteur, mandat_json)

    def save_mandat(self, acteur, json):
        if not isinstance(json['organes']['organeRef'], basestring):
            self.warn(u'Mandat %s à organes multiples, ignoré' % json['uid'])
            return

        mandat = self.get_or_create(Mandat, id_an=json['uid'])

        mandat.acteur = acteur
        mandat.organe = self.get_organe(json['organes']['organeRef'])

        mandat.date_debut = dateparser.parse(json['dateDebut'])
        if json.get('datePublication', None):
            mandat.date_publication = dateparser.parse(json['datePublication'])
        if json.get('dateFin', None):
            mandat.date_fin = dateparser.parse(json['dateFin'])

        mandat.qualite = json['infosQualite']['codeQualite']
        mandat.preseance = int(json['preseance'])
        mandat.nomination_principale = json['nominPrincipale'] == '1'

        if json.get('libelle', None):
            mandat.libelle = json['libelle']

        if json.get('InfosHorsSIAN', None):
            if json['InfosHorsSIAN'].get('HATVP_URI', None):
                mandat.url_hatvp = json['InfosHorsSIAN']['HATVP_URI']

        if 'election' in json:
            el = json['election']
            li = el['lieu']

            mandat.election_region = li['region']
            mandat.election_dept = li['departement']
            mandat.election_dept_num = li['numDepartement']
            mandat.election_cause = el['causeMandat']

            if li['numCirco']:
                mandat.election_circo = int(li['numCirco'])


def run(app, force):
    ImportActeursJob(app).run(force)
