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


@cli.command(short_help=u'Met à jour les organes depuis l\'AN')
@click.option('--force', is_flag=True)
def update_organes_an(force):
    from .parlapi import app
    from .jobs.an_organes import run

    with app.app_context():
        run(app, force)


@cli.command(short_help=u'Met à jour les acteurs depuis l\'AN')
@click.option('--force', is_flag=True)
def update_acteurs_an(force):
    from .parlapi import app
    from .jobs.an_acteurs import run

    with app.app_context():
        run(app, force)


if __name__ == '__main__':
    cli()
