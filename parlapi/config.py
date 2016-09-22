# -*- coding: utf-8 -*-

import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DefaultConfig(object):
    """
    Default parlapi config file for standard environment
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = \
        'postgresql://parlapi:parlapi@localhost:5432/parlapi'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    API_PAGE_SIZE = 10
    SECRET_KEY = 'no-secret-key'


class DebugConfig(DefaultConfig):
    """
    Debug-enabled default config
    """
    DEBUG = True


class AutoSecretKeyConfig(DefaultConfig):
    """
    Default config that automatically generates a secret key in DATA_DIR
    """
    _secret_key = None

    @property
    def SECRET_KEY(self):
        if not self._secret_key:
            secret_file = os.path.join(self.DATA_DIR, 'secret.txt')

            if not os.path.exists(secret_file):
                chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

                from random import SystemRandom
                rnd = SystemRandom()
                key = ''.join([chars[rnd.randint(1, len(chars))-1]
                               for i in range(1, 50)])

                with open(secret_file, 'w+') as f:
                    f.write(key)

            with open(secret_file, 'r') as f:
                self._secret_key = f.read()

        return self._secret_key


class EnvironmentConfig(AutoSecretKeyConfig):
    """
    Config for environment-based setup.
    - PARLAPI_DEBUG: 'True' to enable
    - PARLAPI_DB_URL: database connection URL
    - PARLAPI_DATA_DIR: directory for data files
    - PARLAPI_PAGE_SIZE: default API page size
    """
    DEBUG = os.environ.get('PARLAPI_DEBUG', 'False') == 'True'

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'PARLAPI_DB_URL', DefaultConfig.SQLALCHEMY_DATABASE_URI)

    DATA_DIR = os.environ.get('PARLAPI_DATA_DIR', DefaultConfig.DATA_DIR)
    API_PAGE_SIZE = int(os.environ.get('PARLAPI_PAGE_SIZE',
                                       DefaultConfig.API_PAGE_SIZE))


class OpenshiftConfig(AutoSecretKeyConfig):
    """
    Suitable configuration for use on Openshift
    """
    SQLALCHEMY_DATABASE_URI = \
        'postgresql://%(user)s:%(pass)s@%(host)s:%(port)s/%(name)s' % {
            'name': os.environ.get('OPENSHIFT_APP_NAME', ''),
            'user': os.environ.get('OPENSHIFT_POSTGRESQL_DB_USERNAME', ''),
            'pass': os.environ.get('OPENSHIFT_POSTGRESQL_DB_PASSWORD', ''),
            'host': os.environ.get('OPENSHIFT_POSTGRESQL_DB_HOST', ''),
            'port': os.environ.get('OPENSHIFT_POSTGRESQL_DB_PORT', ''),
        }

    DATA_DIR = os.environ.get('OPENSHIFT_DATA_DIR', '')
