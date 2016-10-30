#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click


@click.group()
def cli():
    pass


@cli.command(short_help=u'Exécute le serveur web flask intégré')
def runserver():
    from .parlapi import app
    app.run()


@cli.command(short_help=u'Crée le schéma BDD')
def createdb():
    from .parlapi import app
    from .models import db

    with app.app_context():
        db.configure_mappers()
        db.create_all()


@cli.command(short_help=u'Supprime le schéma BDD')
def dropdb():
    from .parlapi import app
    from .models import db

    with app.app_context():
        db.drop_all()


@cli.command(short_help=u'Génère un diagramme ER de la BDD')
@click.option('--output')
def erdiagram(output):
    from eralchemy import render_er
    from .parlapi import app
    from .models import db

    with app.app_context():
        render_er(db.Model, output)


@cli.command(short_help=u'Met à jour acteurs, mandats, organes depuis l\'AN')
@click.option('--force', is_flag=True)
@click.option('--file', default=None)
def update_amo_an(force, file):
    from .parlapi import app
    from .jobs.an_amo import run

    with app.app_context():
        app.config.update(SQLALCHEMY_ECHO=False)
        run(app, force, file)


@cli.command(short_help=u'Met à jour dossiers, documents, actes depuis l\'AN')
@click.option('--force', is_flag=True)
@click.option('--file', default=None)
def update_dossiers_an(force, file):
    from .parlapi import app
    from .jobs.an_dossiers import run

    with app.app_context():
        app.config.update(SQLALCHEMY_ECHO=False)
        run(app, force, file)


@cli.command(short_help=u'Met à jour amendements depuis l\'AN')
@click.option('--force', is_flag=True)
@click.option('--file', default=None)
def update_amendements_an(force, file):
    from .parlapi import app
    from .jobs.an_amendements import run

    with app.app_context():
        app.config.update(SQLALCHEMY_ECHO=False)
        run(app, force, file)


@cli.command(short_help=u'Met à jour scrutins depuis l\'AN')
@click.option('--force', is_flag=True)
@click.option('--file', default=None)
def update_scrutins_an(force, file):
    from .parlapi import app
    from .jobs.an_scrutins import run

    with app.app_context():
        app.config.update(SQLALCHEMY_ECHO=False)
        run(app, force, file)


@cli.command(short_help=u'Met à jour réunions depuis l\'AN')
@click.option('--force', is_flag=True)
@click.option('--file', default=None)
def update_reunions_an(force, file):
    from .parlapi import app
    from .jobs.an_reunions import run

    with app.app_context():
        app.config.update(SQLALCHEMY_ECHO=False)
        run(app, force, file)


if __name__ == '__main__':
    cli()
