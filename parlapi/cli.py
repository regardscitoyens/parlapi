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


@cli.command(short_help=u'Crée ou met à jour le schéma BDD')
def createdb():
    from .parlapi import app
    from .models import db

    with app.app_context():
        db.create_all()


@cli.command(short_help=u'Met à jour acteurs, mandats, organes depuis l\'AN')
@click.option('--force', is_flag=True)
def update_amo_an(force):
    from .parlapi import app
    from .jobs.an_amo import run

    with app.app_context():
        run(app, force)


if __name__ == '__main__':
    cli()
