# -*- coding: utf-8 -*-

from builtins import filter
from datetime import datetime
import os
from zipfile import ZipFile

from bs4 import BeautifulSoup
import dateparser
import requests

from ..models import db, Job


class BaseJob(object):
    @property
    def job_name(self):
        raise NotImplementedError()

    @property
    def job(self):
        if not self._job:
            self._job = self.get_or_create(Job, nom=self.job_name)

        return self._job

    def __init__(self, app):
        self.app = app
        self._job = None

    def debug(self, msg):
        self.app.logger.debug('<%s> %s' % (self.job_name, msg))

    def info(self, msg):
        self.app.logger.info('<%s> %s' % (self.job_name, msg))

    def warn(self, msg):
        self.app.logger.warn('<%s> %s' % (self.job_name, msg))

    def error(self, msg):
        self.app.logger.error('<%s> %s' % (self.job_name, msg))

    def get_or_create(self, model, **kwargs):
        item = model.query.filter_by(**kwargs).first()
        if not item:
            item = model(**kwargs)
            db.session.add(item)

        return item

    def update_status(self, status=None, file=None, filedate=None):
        job = self.job
        job.date_exec = datetime.now()
        job.resultat = status or ''

        if file:
            job.url_fichier = file
        if filedate:
            job.date_fichier = filedate

        db.session.commit()


class BaseANJob(BaseJob):
    base_url = 'http://data.assemblee-nationale.fr'

    def __init__(self, app, url):
        super(BaseANJob, self).__init__(app)
        self.url = 'http://data.assemblee-nationale.fr%s' % url

    def parse_json(self, json_filename, json_stream):
        raise NotImplementedError()

    def run(self, ignore_lmd=False):
        self.info(u'Téléchargement %s' % self.url)

        soup = BeautifulSoup(requests.get(self.url).content, 'html5lib')

        def match_link(a):
            return a['href'].endswith('.json.zip')

        try:
            link = next(filter(match_link, soup.select('a[href]')))
        except:
            self.error(u'Lien vers dump JSON introuvable')
            self.update_status('error:json-link')
            return

        jsonzip_url = link['href']
        if jsonzip_url.startswith('/'):
            jsonzip_url = '%s%s' % (self.base_url, jsonzip_url)

        self.info(u'URL JSON zippé : %s' % jsonzip_url)

        try:
            lastmod = requests.head(jsonzip_url).headers['Last-Modified']
        except:
            self.error(u'Date du dump JSON introuvable')
            self.update_status('error:json-lastmod')
            return

        self.info(u'Date modification JSON zippé: %s' % lastmod)

        jsonzip_lmd = dateparser.parse(lastmod)
        if not ignore_lmd:
            if self.job.date_fichier and self.job.date_fichier >= jsonzip_lmd:
                self.info(u'JSON zippé non modifié')
                self.update_status('ok')
                return

        self.info(u'Téléchargement JSON zippé')

        localzip = os.path.join(self.app.config['DATA_DIR'],
                                os.path.basename(jsonzip_url))

        with open(localzip, 'wb') as out:
            r = requests.get(jsonzip_url, stream=True)
            for block in r.iter_content(1024):
                out.write(block)

        with ZipFile(localzip, 'r') as z:
            for f in [f for f in z.namelist() if f.endswith('.json')]:
                self.info(u'JSON extrait : %s' % f)
                with z.open(f) as zf:
                    try:
                        self.parse_json(f, zf)
                    except Exception, e:
                        self.error(u'Erreur: %s' % e)

        self.info(u'Job terminé')
        self.update_status('ok', jsonzip_url, jsonzip_lmd)
