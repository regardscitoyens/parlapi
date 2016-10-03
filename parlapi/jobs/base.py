# -*- coding: utf-8 -*-

from datetime import datetime
import os
import traceback
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

    def __init__(self, app, flush_every=1000):
        self.app = app
        self.current = None
        self._job = None
        self._start = datetime.now()
        self._count = 0
        self._flush_every = 1000

    def debug(self, msg):
        self.app.logger.debug('<%s> %s' % (self.job_name, msg))

    def info(self, msg):
        self.app.logger.info('<%s> %s' % (self.job_name, msg))

    def warn(self, msg):
        self.app.logger.warn('<%s> %s' % (self.job_name, msg))

    def error(self, msg):
        self.app.logger.error('<%s> %s' % (self.job_name, msg))

    def parse_date(self, date):
        if not date:
            return None
        elif len(date) >= 19:
            return dateparser.parse(date[0:19])
        else:
            return dateparser.parse(date[0:10])

    def get_or_create(self, model, **kwargs):
        item = model.query.filter_by(**kwargs).first()
        if not item:
            if self._count > 0 and self._count % 1000 == 0:
                db.session.commit()

            item = model(**kwargs)
            db.session.add(item)

        self._count += 1
        if self._count % self._flush_every == 0:
            self.debug('%d objects touched, flushing' % self._count)
            db.session.flush()

        return item

    def update_status(self, status=None, file=None, filedate=None):
        job = self.job
        job.date_exec = datetime.now()
        job.temps_exec = (datetime.now() - self._start).seconds
        job.nb_items = self._count
        job.resultat = status or u''

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

    def handle_json(self, filename, filestream):
        try:
            self.current = None
            self.parse_json(filename, filestream)
            return True
        except Exception, e:
            if self.current:
                msg = 'Erreur (%s)' % self.current
            else:
                msg = 'Erreur'
            stack = ''.join(traceback.format_exc())
            self.error(u'%s: %s\n%s' % (msg, e, stack))
            self.update_status(u'error:parse-json')
            return False

    def run(self, ignore_lmd=False, file=None):
        if file:
            self.info(u'Exécution avec fichier %s' % file)
            with open(file) as f:
                if not self.handle_json(os.path.basename(file), f):
                    return
            db.session.commit()
            self.info(u'Job terminé')
            return

        self.info(u'Téléchargement %s' % self.url)

        try:
            soup = BeautifulSoup(requests.get(self.url).content, 'html5lib')
        except:
            self.error(u'Téléchargement %s impossible' % self.url)
            self.update_status(u'error:download-html')
            return

        def match_link(a):
            return a['href'].endswith('.json.zip')

        try:
            link = [a for a in soup.select('a[href]') if match_link(a)][0]
        except:
            self.error(u'Lien vers dump .json.zip introuvable')
            self.update_status(u'error:zip-link')
            return

        jsonzip_url = link['href']
        if jsonzip_url.startswith('/'):
            jsonzip_url = '%s%s' % (self.base_url, jsonzip_url)

        self.info(u'URL JSON zippé : %s' % jsonzip_url)

        try:
            lastmod = requests.head(jsonzip_url).headers['Last-Modified']
        except:
            self.error(u'Date du dump .json.zip introuvable')
            self.update_status(u'error:zip-lastmod')
            return

        self.info(u'Date modification dump .json.zip: %s' % lastmod)

        jsonzip_lmd = dateparser.parse(lastmod)
        if not ignore_lmd:
            if self.job.date_fichier and self.job.date_fichier >= jsonzip_lmd:
                self.info(u'Dump .json.zip non modifié')
                self.update_status(u'ok')
                return

        self.info(u'Téléchargement .json.zip')

        localzip = os.path.join(self.app.config['DATA_DIR'],
                                os.path.basename(jsonzip_url))

        try:
            with open(localzip, 'wb') as out:
                r = requests.get(jsonzip_url, stream=True)
                for block in r.iter_content(1024):
                    out.write(block)
        except:
            self.error(u'Téléchargement .json.zip')
            self.update_status(u'error:zip-download')
            return

        try:
            with ZipFile(localzip, 'r') as z:
                for f in [f for f in z.namelist() if f.endswith('.json')]:
                    self.info(u'JSON extrait : %s' % f)
                    with z.open(f) as zf:
                        if not self.handle_json(f, zf):
                            return

        except:
            self.error(u'Ouverture ZIP impossible')
            self.update_status(u'error:zip-open')
            return

        self.info(u'Job terminé')
        self.update_status(u'ok', jsonzip_url, jsonzip_lmd)
