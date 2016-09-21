ParlAPI
=======

L'objectif de ParlAPI est de fournir une API réellement utilisable sur l'Open
Data parlementaire.

Les données proviennent des portails Open Data parlementaires :
* [data.assemblee-nationale.fr](http://data.assemblee-nationale.fr/)
* [data.senat.fr](http://data.senat.fr/)
 
ParlAPI est conçu de manière à respecter le plus fidèlement possible le schéma
de données des sources parlementaires.  En particulier, aucune donnée calculée 
n'est ajoutée au modèle.

## Installation

### Prérequis

- Python 2.7
- PostgreSQL 9.2+
- pip
- virtualenv

### Installation

```bash
$ git clone https://github.com/njoyard/parlapi
$ cd parlapi
$ virtualenv ve
$ source ve/bin/activate
$ pip install -e .
$ psql -c "create user parlapi with password 'parlapi';"
$ psql -c "create database parlapi with owner parlapi;"
```

### Utilisation

```bash
$ parlapi createdb
$ parlapi update_organes_an
$ parlapi update_acteurs_an
$ parlapi runserver
```
