# -*- coding: utf-8 -*-

from .base import BaseANJob
from .utils import ijson_items
from ..models import (Organe, Legislature, Acteur, Mandat, Scrutin, Votant,
                      ScrutinGroupe)


class ImportScrutinsJob(BaseANJob):

    positions = {
        'nonVotants': u'non-votant',
        'pours': u'pour',
        'contres': u'contre',
        'abstentions': u'abstention'
    }

    def __init__(self, app, name, url):
        self._job_name = name
        super(ImportScrutinsJob, self).__init__(app, url)

    @property
    def job_name(self):
        return self._job_name

    def parse_json(self, filename, stream):
        scrutin = 'scrutins.scrutin.item'

        for prefix, obj in ijson_items(stream, [scrutin]):
            self.save_scrutin(obj)

    def save_scrutin(self, json):
        self.current = u'Scrutin %s' % json['uid']
        scrutin, _ = self.get_or_create(Scrutin, id=json['uid'])

        scrutin.numero = int(json['numero'])
        scrutin.date = self.parse_date(json['dateScrutin'])
        scrutin.quantieme_jour_seance = int(json['quantiemeJourSeance'])
        scrutin.titre = json['titre']
        scrutin.demandeur = json['demandeur']['texte']
        scrutin.objet = json['objet']['libelle']

        scrutin.type_code = json['typeVote']['codeTypeVote']
        scrutin.type_libelle = json['typeVote']['libelleTypeVote']
        scrutin.type_majorite = json['typeVote']['typeMajorite']

        scrutin.sort_code = json['sort']['code']
        scrutin.sort_libelle = json['sort']['libelle']

        scrutin.mode_publication = json['modePublicationDesVotes']

        sy = json['syntheseVote']
        scrutin.synthese_votants = int(sy['nombreVotants'])
        scrutin.synthese_exprimes = int(sy['suffragesExprimes'])
        scrutin.synthese_requis = int(sy['nbrSuffragesRequis'])
        scrutin.synthese_pour = int(sy['decompte']['pour'])
        scrutin.synthese_contre = int(sy['decompte']['contre'])
        scrutin.synthese_abstention = int(sy['decompte']['abstention'])
        scrutin.synthese_nonvotant = int(sy['decompte']['nonVotant'])

        scrutin.legislature = self.get_cached(Legislature,
            int(json['legislature']))
        scrutin.organe = self.get_cached(Organe, json['organeRef'])

        gr = json['ventilationVotes']['organe']['groupes']['groupe']
        scrutin.groupes = [self.save_groupe(g) for g in gr]

    def save_groupe(self, json):
        cur = self.current
        self.current = u'%s > groupe %s' % (cur, json['organeRef'])

        groupe = ScrutinGroupe()

        groupe.organe = self.get_cached(Organe, json['organeRef'])
        groupe.nombre_membres = int(json['nombreMembresGroupe'])

        vote = json['vote']
        groupe.position_majoritaire = vote['positionMajoritaire']
        groupe.decompte_pour = int(vote['decompteVoix']['pour'])
        groupe.decompte_contre = int(vote['decompteVoix']['contre'])
        groupe.decompte_abstention = int(vote['decompteVoix']['abstention'])

        if 'nonVotant' in vote['decompteVoix']:
            groupe.decompte_nonvotant = int(vote['decompteVoix']['nonVotant'])
        else:
            groupe.decompte_nonvotant = 0

        votants = []
        for k, pos in self.positions.items():
            if vote['decompteNominatif'].get(k, None):
                if isinstance(vote['decompteNominatif'][k], basestring):
                    continue

                vs = vote['decompteNominatif'][k]['votant']
                if isinstance(vs, dict):
                    vs = [vs]

                for v in vs:
                    votants.append(Votant(position=pos,
                                   acteur=self.get_cached(Acteur, v['acteurRef']),
                                   mandat=self.get_cached(Mandat, v['mandatRef']),
                                   cause=v.get('causePositionVote', None)))
        groupe.votants = votants

        self.current = cur
        return groupe


def run(app, force=False, file=None):
    ImportScrutinsJob(
        app,
        u'AN: scrutins',
        '/travaux-parlementaires/votes'
    ).run(force, file)
