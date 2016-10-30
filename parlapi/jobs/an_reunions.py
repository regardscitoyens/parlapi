# -*- coding: utf-8 -*-

from .base import BaseANJob
from .utils import ijson_items
from ..models import (Organe, Acteur, Reunion, ODJItem, ODJPoint,
                      OrganeReunion, ActeurReunion)


class ImportReunionsJob(BaseANJob):

    def __init__(self, app, name, url):
        self._job_name = name
        super(ImportReunionsJob, self).__init__(app, url)

    @property
    def job_name(self):
        return self._job_name

    def parse_json(self, filename, stream):
        reunion = 'reunions.reunion.item'

        for prefix, obj in ijson_items(stream, [reunion]):
            self.save_reunion(obj)

    def save_reunion(self, json):
        self.current = u'Reunion %s' % json['uid']
        reunion, _ = self.get_or_create(Reunion, id=json['uid'])

        if json.get('typeReunion', None):
            reunion.type_reunion = json['typeReunion']

        if json.get('timeStampDebut', None):
            reunion.date_debut = self.parse_date(json['timeStampDebut'])

        if json.get('timeStampFin', None):
            reunion.date_fin = self.parse_date(json['timeStampFin'])

        if json['lieu'].get('code', None):
            reunion.lieu_code = json['lieu']['code']
        reunion.lieu_libelle = json['lieu']['libelleLong']

        if json.get('cycleDeVie', None):
            cdv = json['cycleDeVie']
            reunion.etat = cdv['etat']
            reunion.date_creation = self.parse_date(cdv['chrono']['creation'])
            reunion.date_cloture = self.parse_date(cdv['chrono']['cloture'])

        if json.get('identifiants', None):
            ids = json['identifiants']
            reunion.seance_id_jo = ids['idJO']
            reunion.seance_quantieme = ids['quantieme']
            reunion.seance_date = self.parse_date(ids['DateSeance'])

        acteurs = []
        organes = []

        demandeurs = json.get('demandeurs', None) or {}

        if 'acteur' in demandeurs:
            acts = demandeurs['acteur']
            if isinstance(acts, dict):
                acts = [acts]

            for act in acts:
                ar = ActeurReunion(relation=u'demandeur')
                ar.acteur = self.get_cached(Acteur, act['acteurRef'])
                acteurs.append(ar)

        # SRSLY WTF !? I don't want to live on this planet anymore D:<
        if json.get('demandeur', None) and 'acteurRef' in json['demandeur']:
            ar = ActeurReunion(relation=u'demandeur')
            ar.acteur = self.get_cached(Acteur, json['demandeur']['acteurRef'])
            acteurs.append(ar)

        if 'organe' in demandeurs:
            orgs = demandeurs['organe']
            if isinstance(orgs, dict):
                orgs = [orgs]

            for org in orgs:
                or_ = OrganeReunion(relation=u'demandeur')
                or_.organe = self.get_cached(Organe, org['organeRef'])
                organes.append(or_)

        if json.get('organeReuniRef', None):
            or_ = OrganeReunion(relation=u'organeReuni')
            or_.organe = self.get_cached(Organe, json['organeReuniRef'])
            organes.append(or_)

        reunion.organes = organes

        prt = json.get('participants', None) or {}
        pri = prt.get('participantsInternes', None)
        if pri:
            pris = pri.get('participantInterne', None) or []
            if isinstance(pris, dict):
                pris = [pris]
            for p in pris:
                ar = ActeurReunion(relation=u'participant', presence=p['presence'])
                ar.acteur = self.get_cached(Acteur, p['acteurRef'])
                acteurs.append(ar)

        pra = prt.get('personnesAuditionnees', None)
        if pra:
            pras = pra.get('personneAuditionnee', None) or []
            if isinstance(pras, dict):
                pras = [pras]
            for p in pras:
                ar = ActeurReunion(relation=u'auditionne')
                act, created = self.get_cached_(Acteur, p['uid']['#text'])

                if created and p['uid']['@xsi:type'] == 'IdPersonneExterne_type':
                    # Pour les acteurs interne le job AMO remplit ces infos
                    act.civilite = p['ident']['civ']
                    act.nom = p['ident']['nom']
                    act.prenom = p['ident']['prenom']
                    act.date_naissance = self.parse_date(p['dateNais'])

                ar.acteur = act
                acteurs.append(ar)

        reunion.acteurs = acteurs

        if json.get('resumeODJ', {}).get('items', None):
            items = json['resumeODJ']['items']
            if isinstance(items, basestring):
                items = [items]
            reunion.items_odj = [ODJItem(item=i) for i in items]

        if json.get('pointsODJ', {}).get('pointsODJ', None):
            points = json['pointsODJ']['pointODJ']
            if isinstance(points, dict):
                points = [points]
            reunion.points_odj = [self.save_point(p) for p in points]

    def save_point(self, json):
        cur = self.current
        self.current = '%s > Point %s' % (cur, jon['uid'])

        point, _ = self.get_or_create(ODJPoint, id=json['uid'])

        point.objet = json['objet']
        point.type = json['typePointODJ']
        point.procedure = json['procedure']
        point.nature_travaux = json['natureTravauxODJ']
        point.date_conf_presse = self.parse_date(json['dateConfPres'])

        if json.get('comiteSecret', None):
            point.comite_secret = json['comiteSecret'] == 'true'
        if json.get('ouverturePresse', None):
            point.ouverture_presse = json['ouverturePresse'] == 'true'

        cdv = json['cycleDeVie']
        point.etat = cdv['etat']
        point.date_creation = self.parse_date(cdv['chrono']['creation'])
        point.date_cloture = self.parse_date(cdv['chrono']['cloture'])

        if json.get('dossierLegislatifsRefs', None):
            dossiers = json['dossierLegislatifsRefs']
            if isinstance(dossier, dict):
                dossiers = [dossiers]
            point.dossiers = [self.get_cached(Dossier, d['dossierRef'])
                              for d in dossiers]

        self.current = cur
        return point


def run(app, force=False, file=None):
    ImportReunionsJob(
        app,
        u'AN: réunions',
        '/reunions/reunions'
    ).run(force, file)
