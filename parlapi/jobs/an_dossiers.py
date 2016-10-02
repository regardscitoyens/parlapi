# -*- coding: utf-8 -*-

from .base import BaseANJob
from .utils import ijson_items
from ..models import (Organe, Legislature, Acteur, Document, Theme,
                      ActeurDocument, OrganeDocument, Dossier, Acte)


class ImportDossiersJob(BaseANJob):
    cache_legislatures = {}
    cache_acteurs = {}
    cache_organes = {}
    cache_themes = {}
    cache_dossiers = {}
    cache_documents = {}

    def __init__(self, app, name, url):
        self._job_name = name
        super(ImportDossiersJob, self).__init__(app, url)

    @property
    def job_name(self):
        return self._job_name

    def get_legislature(self, num):
        if num not in self.cache_legislatures:
            self.cache_legislatures[num] = self.get_or_create(
                Legislature, id=int(num))

        return self.cache_legislatures[num]

    def get_theme(self, theme):
        if theme not in self.cache_themes:
            self.cache_themes[theme] = self.get_or_create(Theme, theme=theme)

        return self.cache_themes[theme]

    def get_acteur(self, id):
        if id not in self.cache_acteurs:
            self.cache_acteurs[id] = self.get_or_create(Acteur, id=id)

        return self.cache_acteurs[id]

    def get_organe(self, id):
        if id not in self.cache_organes:
            self.cache_organes[id] = self.get_or_create(
                Organe, id=id)

        return self.cache_organes[id]

    def get_dossier(self, id):
        if id not in self.cache_dossiers:
            self.cache_dossiers[id] = self.get_or_create(
                Dossier, id=id)

        return self.cache_dossiers[id]

    def get_document(self, id):
        if id not in self.cache_documents:
            self.cache_documents[id] = self.get_or_create(
                Document, id=id)

        return self.cache_documents[id]

    def parse_json(self, filename, stream):
        document = 'export.textesLegislatifs.document.item'
        dossier = 'export.dossiersLegislatifs.dossier.item'

        for prefix, obj in ijson_items(stream, [document, dossier]):
            if prefix == document:
                self.save_document(obj)
            if prefix == dossier:
                self.save_dossier(obj['dossierParlementaire'])

    def save_document(self, json, chaine=[]):
        if json['uid'] in chaine:
            self.warn(
                u'Dépendance circulaire sur documents: %s > %s' %
                (' > '.join(chaine), json['uid'])
            )
            return None

        chaine.append(json['uid'])

        self.current = 'Document %s' % json['uid']
        document = self.get_document(json['uid'])

        chrono = json['cycleDeVie']['chrono']
        document.date_creation = self.parse_date(chrono['dateCreation'])
        document.date_depot = self.parse_date(chrono['dateDepot'])
        document.date_publication = self.parse_date(chrono['datePublication'])
        document.date_publication_web = \
            self.parse_date(chrono['datePublicationWeb'])

        document.titre = json['titres']['titrePrincipal']
        document.denomination_structurelle = json['denominationStructurelle']

        klass = json['classification']
        if klass.get('type', None):
            document.type_code = klass['type']['code']
            document.type_libelle = klass['type']['libelle']
        if klass.get('sousType', None):
            document.soustype_code = klass['sousType']['code']
            document.soustype_libelle = klass['sousType'].get('libelle', None)
        document.statut_adoption = klass['statutAdoption']

        acteurs = []
        organes = []

        auteurs = json['auteurs']['auteur']
        if isinstance(auteurs, dict):
            auteurs = [auteurs]

        for auteur in auteurs:
            if 'acteur' in auteur:
                qual = auteur['acteur'].get('qualite', None)
                ad = ActeurDocument(relation=u'auteur', qualite=qual)
                ad.acteur = self.get_acteur(auteur['acteur']['acteurRef'])
                acteurs.append(ad)
            elif 'organe' in auteur:
                od = OrganeDocument(relation=u'auteur')
                od.organe = self.get_organe(auteur['organe']['organeRef'])
                organes.append(od)
            else:
                self.warn(u'Ignoré type auteur inconnu dans %s' % self.current)

        if json.get('coSignataires', None):
            cosign = json['coSignataires']['coSignataire']
            if isinstance(cosign, dict):
                cosign = [cosign]

            for auteur in cosign:
                dc = self.parse_date(auteur['dateCosignature'])
                if auteur.get('dateRetraitCosignature', None):
                    dr = self.parse_date(auteur['dateRetraitCosignature'])
                else:
                    dr = None

                if 'acteur' in auteur:
                    ad = ActeurDocument(relation=u'cosignataire',
                                        date_cosignature=dc,
                                        date_retrait_cosignature=dr)
                    ad.acteur = self.get_acteur(auteur['acteur']['acteurRef'])
                    acteurs.append(ad)
                elif 'organe' in auteur:
                    od = OrganeDocument(relation=u'cosignataire',
                                        date_cosignature=dc,
                                        date_retrait_cosignature=dr)
                    od.organe = self.get_organe(auteur['organe']['organeRef'])
                    organes.append(od)

        document.acteurs = acteurs
        document.organes = organes

        if json.get('legislature', None):
            document.legislature = self.get_legislature(json['legislature'])

        if 'dossierRef' in json:
            document.dossier = self.get_dossier(json['dossierRef'])

        if json.get('indexation', None):
            document.themes = [self.get_theme(
                json['indexation']['themes']['theme']['libelleTheme'])]

        if json.get('divisions', None):
            divs = json['divisions']['division']
            if isinstance(divs, dict):
                divs = [divs]

            document.divisions = [div for div in
                                  [self.save_document(d, chaine) for d in divs]
                                  if div]

        chaine.pop()

        return document

    def save_dossier(self, json):
        self.current = 'Dossier %s' % json['uid']
        dossier = self.get_dossier(json['uid'])

        dossier.legislature = self.get_legislature(json['legislature'])

        td = json['titreDossier']
        dossier.titre = td.get('titre', None)
        dossier.titre_chemin = td['titreChemin']
        dossier.senat_chemin = td['senatChemin']

        pp = json['procedureParlementaire']
        dossier.procedure_code = int(pp['code'])
        dossier.procedure_libelle = pp['libelle']

        # TODO initiateur(s)

        if json.get('actesLegislatifs', None):
            json_actes = json['actesLegislatifs']['acteLegislatif']
            if isinstance(json_actes, dict):
                json_actes = [json_actes]

            dossier.actes_legislatifs = [self.save_acte(j) for j in json_actes]
        else:
            dossier.actes_legislatifs = []

        return dossier

    def save_acte(self, json):
        self.current = 'Acte %s' % json['uid']
        acte = self.get_or_create(Acte, id=json['uid'])

        acte.code = json['codeActe']
        acte.libelle = json['libelleActe']['nomCanonique']

        if json.get('date', None):
            acte.date = self.parse_date(json['date'])
        elif json.get('dateActe', None):
            acte.date = self.parse_date(json['dateActe'])

        if json.get('actesLegislatifs', None):
            json_actes = json['actesLegislatifs']['acteLegislatif']
            if isinstance(json_actes, dict):
                json_actes = [json_actes]

            acte.actes = [self.save_acte(j) for j in json_actes]
        else:
            acte.actes = []

        if json.get('organeRef', None):
            acte.organe = self.get_organe(json['organeRef'])

        if json.get('texteAssocie', None):
            acte.document = self.get_document(json['texteAssocie'])

        return acte


def run(app, force=False, file=None):
    ImportDossiersJob(
        app,
        u'AN: dossiers législatifs',
        '/travaux-parlementaires/dossiers-legislatifs'
    ).run(force, file)
