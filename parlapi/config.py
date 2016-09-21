# -*- coding: utf-8 -*-

import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DefaultConfig(object):
    DEBUG = False
    SECRET_KEY = 'not secret'
    SQLALCHEMY_DATABASE_URI = \
        'postgresql://parlapi:parlapi@localhost:5432/parlapi'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    API_PAGE_SIZE = 10


class DebugConfig(DefaultConfig):
    DEBUG = True


if 'OPENSHIFT_APP_NAME' in os.environ:
    class OpenshiftConfig(DefaultConfig):
        SQLALCHEMY_DATABASE_URI = \
            'postgresql://%(user)s:%(pass)s@%(host)s:%(port)s/%(name)s' % {
                'name': os.environ['OPENSHIFT_APP_NAME'],
                'user': os.environ['OPENSHIFT_POSTGRESQL_DB_USERNAME'],
                'pass': os.environ['OPENSHIFT_POSTGRESQL_DB_PASSWORD'],
                'host': os.environ['OPENSHIFT_POSTGRESQL_DB_HOST'],
                'port': os.environ['OPENSHIFT_POSTGRESQL_DB_PORT'],
            }

        DATA_DIR = os.environ['OPENSHIFT_DATA_DIR']

        SECRET_FILE = os.path.join(DATA_DIR, 'secret.txt')
        if not os.path.exists(SECRET_FILE):
            chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

            from random import SystemRandom
            rnd = SystemRandom()
            key = ''.join([chars[rnd.randint(1, len(chars))-1]
                           for i in range(1, 50)])

            with open(SECRET_FILE, 'w+') as f:
                f.write(key)

        with open(SECRET_FILE, 'r') as f:
            SECRET_KEY = f.read()
