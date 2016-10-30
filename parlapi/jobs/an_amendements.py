# -*- coding: utf-8 -*-

from .base import BaseANJob
from .utils import ijson_items
from ..models import Acteur, Amendement, Document, Legislature, Organe


class ImportAmendementsJob(BaseANJob):

    def __init__(self, app, name, url):
        self._job_name = name
        super(ImportAmendementsJob, self).__init__(app, url)

    @property
    def job_name(self):
        return self._job_name

    def parse_json(self, filename, stream):
        texte = 'textesEtAmendements.texteleg.item'

        for prefix, obj in ijson_items(stream, [texte]):
            if prefix == texte:
                self.save_texte(obj)

    def save_texte(self, json):
        self.current = u'Texte %s' % json['refTexteLegislatif']
        document = self.get_cached(Document, json['refTexteLegislatif'])

        amendements = json['amendements']['amendement']
        if isinstance(amendements, dict):
            amendements = [amendements]

        for am in amendements:
            self.save_amendement(am, document)

    def save_amendement(self, json, document):
        self.current = u'Amendement %s' % json['uid']
        am = self.get_cached(Amendement, json['uid'])

        am.document = document

        id = json['identifiant']
        am.numero = int(id['numero'])
        am.num_rect = int(id['numRect'])
        am.organe = self.get_cached(Organe, id['saisine']['organeExamen'])
        am.legislature = self.get_cached(Legislature, int(id['legislature']))
        am.numero_long = json['numeroLong']
        am.etape_texte = json['etapeTexte']
        am.tri = json['triAmendement']
        am.cardinal_multiples = int(json['cardinaliteAmdtMultiples'])

        if json.get('amendementParent', None):
            am.amendement_parent = \
                self.get_cached(Amendement, json['amendementParent'])

        am.etat = json['etat']
        am.article_99 = int(json['article99']) > 0

        so = json['sort']
        if so:
            am.sort = so['sortEnSeance']
            am.date_sort = self.parse_date(so['dateSaisie'])

        fr = json['pointeurFragmentTexte']
        dv = fr['division']
        am.division_texte = dv['titre']
        am.division_position = dv['avant_A_Apres']

        am.division_chapitre_additionnel = \
            dv.get('chapitreAdditionnel', '0') != '0'
        am.division_article_additionnel = \
            dv.get('articleAdditionnel', '0') != '0'
        al = fr['alinea']
        if al and al.get('numero', None):
            am.division_alinea = int(al['numero'])
            am.division_alinea_position = al['avant_A_Apres']

        co = json['corps']
        am.corps_dispositif = co.get('dispositif', None)
        am.corps_expose = co.get('exposeSommaire', None)

        lo = json['loiReference']
        am.code_loi = lo['codeLoi']
        am.code_loi_division = lo['divisionCodeLoi']

        am.date_depot = self.parse_date(json['dateDepot'])
        am.date_distribution = self.parse_date(json['dateDistribution'])


def run(app, force=False, file=None):
    ImportAmendementsJob(
        app,
        u'AN: amendements',
        '/travaux-parlementaires/amendements'
    ).run(force, file)
