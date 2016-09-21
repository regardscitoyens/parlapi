# -*- coding: utf-8 -*-

import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config(object):
    DEBUG = False
    SECRET_KEY = 'not secret'
    SQLALCHEMY_DATABASE_URI = \
        'postgresql://parlapi:parlapi@localhost:5432/parlapi'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATA_DIR = os.path.join(BASE_DIR, 'data')


class DebugConfig(Config):
    DEBUG = True


CurrentConfig = DebugConfig
