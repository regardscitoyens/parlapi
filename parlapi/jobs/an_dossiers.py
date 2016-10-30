# -*- coding: utf-8 -*-

from .base import BaseANJob
from .utils import ijson_items
from ..models import (Organe, Legislature, Acteur, Document, Theme, Mandat,
                      ActeurDocument, OrganeDocument, Dossier, ActeurDossier,
                      OrganeDossier, Acte)


class ImportDossiersJob(BaseANJob):

    def __init__(self, app, name, url):
        self._job_name = name
        super(ImportDossiersJob, self).__init__(app, url)

    @property
    def job_name(self):
        return self._job_name

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

        self.current = u'Document %s' % json['uid']
        document = self.get_cached(Document, json['uid'])

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
                ad.acteur = self.get_cached(Acteur, auteur['acteur']['acteurRef'])
                acteurs.append(ad)
            elif 'organe' in auteur:
                od = OrganeDocument(relation=u'auteur')
                od.organe = self.get_cached(Organe, auteur['organe']['organeRef'])
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
                    ad.acteur = self.get_cached(Acteur,
                        auteur['acteur']['acteurRef'])
                    acteurs.append(ad)
                elif 'organe' in auteur:
                    od = OrganeDocument(relation=u'cosignataire',
                                        date_cosignature=dc,
                                        date_retrait_cosignature=dr)
                    od.organe = self.get_cached(Organe,
                        auteur['organe']['organeRef'])
                    organes.append(od)

        document.acteurs = acteurs
        document.organes = organes

        if json.get('legislature', None):
            document.legislature = self.get_cached(Legislature,
                int(json['legislature']))

        if 'dossierRef' in json:
            document.dossier = self.get_cached(Dossier, json['dossierRef'])

        if json.get('indexation', None):
            document.themes = [self.get_cached(Theme,
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
        self.current = u'Dossier %s' % json['uid']
        dossier = self.get_cached(Dossier, json['uid'])

        dossier.legislature = self.get_cached(Legislature,
            int(json['legislature']))

        td = json['titreDossier']
        dossier.titre = td.get('titre', None)
        dossier.titre_chemin = td['titreChemin']
        dossier.senat_chemin = td['senatChemin']

        pp = json['procedureParlementaire']
        dossier.procedure_code = int(pp['code'])
        dossier.procedure_libelle = pp['libelle']

        acteursdossier = []
        organesdossier = []

        if json.get('initiateur', None):
            if json['initiateur'].get('acteurs', None):
                acteurs = json['initiateur']['acteurs']['acteur']
                if isinstance(acteurs, dict):
                    acteurs = [acteurs]
                for acteur in acteurs:
                    ad = ActeurDossier(relation=u'initiateur')
                    ad.acteur = self.get_cached(Acteur, acteur['acteurRef'])
                    ad.mandat = self.get_cached(Mandat, acteur['mandatRef'])
                    acteursdossier.append(ad)
            if json['initiateur'].get('organes', None):
                organes = json['initiateur']['organes']['organe']
                if isinstance(organes, dict):
                    organes = [organes]
                for organe in organes:
                    od = OrganeDossier(relation=u'initiateur')
                    od.organe = self.get_cached(Organe, organe['organeRef']['uid'])
                    organesdossier.append(od)

        dossier.acteurs = acteursdossier
        dossier.organes = organesdossier

        if json.get('actesLegislatifs', None):
            json_actes = json['actesLegislatifs']['acteLegislatif']
            if isinstance(json_actes, dict):
                json_actes = [json_actes]

            dossier.actes_legislatifs = [self.save_acte(j) for j in json_actes]
        else:
            dossier.actes_legislatifs = []

        return dossier

    def save_acte(self, json):
        self.current = u'Acte %s' % json['uid']
        acte = self.get_cached(Acte, json['uid'])

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
            acte.organe = self.get_cached(Organe, json['organeRef'])

        if json.get('texteAssocie', None):
            acte.document = self.get_cached(Document, json['texteAssocie'])

        return acte


def run(app, force=False, file=None):
    ImportDossiersJob(
        app,
        u'AN: dossiers législatifs',
        '/travaux-parlementaires/dossiers-legislatifs'
    ).run(force, file)
