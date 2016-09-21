Requirements
- python 2.7
- postgresql 9.2+
- virtualenv

Installation
- git clone
- cd parlapi
- virtualenv ve
- source ve/bin/activate
- pip install -e .
- psql -c "create user parlapi with password 'parlapi';"
- psql -c "create database parlapi with owner parlapi;"

Usage:
- parlapi createdb
- parlapi update_organes_an
- parlapi update_acteurs_an
- parlapi runserver
-