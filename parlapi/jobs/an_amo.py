# -*- coding: utf-8 -*-

from .base import BaseANJob
from .utils import ijson_items
from ..models import Organe, Regime, Legislature, Acteur, Mandat


class ImportAMOJob(BaseANJob):
    cache_organes = {}
    cache_legislatures = {}
    cache_regimes = {}

    def __init__(self, app, name, url):
        self._job_name = name
        super(ImportAMOJob, self).__init__(app, url)

    @property
    def job_name(self):
        return self._job_name

    def parse_json(self, filename, stream):
        acteur = 'export.acteurs.acteur.item'
        organe = 'export.organes.organe.item'

        for prefix, obj in ijson_items(stream, [organe, acteur]):
            if prefix == acteur:
                self.save_acteur(obj)
            elif prefix == organe:
                self.save_organe(obj)

    def get_organe(self, id):
        if id not in self.cache_organes:
            self.cache_organes[id] = self.get_or_create(
                Organe, id=id)

        return self.cache_organes[id]

    def get_regime(self, nom):
        if nom not in self.cache_regimes:
            self.cache_regimes[nom] = self.get_or_create(
                Regime, nom=nom)

        return self.cache_regimes[nom]

    def get_legislature(self, num):
        if num not in self.cache_legislatures:
            self.cache_legislatures[num] = self.get_or_create(
                Legislature, id=int(num))

        return self.cache_legislatures[num]

    def save_acteur(self, json):
        self.current = 'Acteur %s' % json['uid']['#text']
        acteur = self.get_or_create(Acteur, id=json['uid']['#text'])

        ec = json['etatCivil']
        id = ec['ident']

        acteur.civilite = id['civ']
        acteur.nom = id['nom']
        acteur.prenom = id['prenom']

        nais = ec['infoNaissance']

        acteur.date_naissance = self.parse_date(nais['dateNais'])
        acteur.ville_naissance = nais['villeNais']
        acteur.dept_naissance = nais['depNais']
        acteur.pays_naissance = nais['paysNais']

        if ec.get('dateDeces', None):
            acteur.date_deces = self.parse_date(ec['dateDeces'])

        if 'profession' in json:
            pro = json['profession']

            acteur.profession = pro['libelleCourant']
            acteur.profession_cat_insee = pro['socProcINSEE']['catSocPro']
            acteur.profession_fam_insee = pro['socProcINSEE']['famSocPro']

        for mandat_json in json['mandats']['mandat']:
            self.save_mandat(acteur, mandat_json)

    def save_mandat(self, acteur, json):
        self.current = 'Mandat %s' % json['uid']
        mandat = self.get_or_create(Mandat, id=json['uid'])

        mandat.acteur = acteur

        if isinstance(json['organes']['organeRef'], basestring):
            organe_refs = [json['organes']['organeRef']]
        else:
            organe_refs = json['organes']['organeRef']

        mandat.organes = [self.get_organe(ref) for ref in organe_refs]

        mandat.date_debut = self.parse_date(json['dateDebut'])
        if json.get('datePublication', None):
            mandat.date_publication = self.parse_date(json['datePublication'])
        if json.get('dateFin', None):
            mandat.date_fin = self.parse_date(json['dateFin'])

        mandat.qualite = json['infosQualite']['codeQualite']
        mandat.nomination_principale = json['nominPrincipale'] == '1'

        if json.get('preseance', None):
            mandat.preseance = int(json['preseance'])

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

    def save_organe(self, json):
        self.current = 'Organe %s' % json['uid']
        organe = self.get_organe(json['uid'])

        organe.type = json['codeType']
        organe.libelle = json['libelle']
        organe.libelle_court = json['libelleAbrege']
        organe.abbreviation = json['libelleAbrev']

        if json['viMoDe']['dateDebut']:
            organe.date_debut = self.parse_date(json['viMoDe']['dateDebut'])
        else:
            organe.date_debut = None

        if json['viMoDe']['dateFin']:
            organe.date_fin = self.parse_date(json['viMoDe']['dateFin'])
        else:
            organe.date_fin = None

        if json.get('regime', None):
            organe.regime = self.get_regime(json['regime'])

        if json.get('legislature', None):
            organe.legislature = self.get_legislature(json['legislature'])
            if organe.regime:
                organe.legislature.regime = organe.regime


def run(app, force=False, file=None):
    if file:
        ImportAMOJob(app, u'AN: députés (historique)', '').run(force, file)
    else:
        ImportAMOJob(app, u'AN: députés-sénateurs-ministres',
                     '/acteurs/deputes-senateurs-ministres').run(force)
        ImportAMOJob(app, u'AN: députés (historique)',
                     '/acteurs/historique-des-deputes').run(force)
