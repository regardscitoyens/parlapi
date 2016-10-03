import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="parlapi",
    version="0.0.1",
    author="Nicolas Joyard",
    author_email="joyard.nicolas@gmail.com",
    description=("A browsable API over French parliament data dumps"),
    license="MIT",
    keywords="django politics open data france french parliament senat assemblee nationale",
    url="https://github.com/njoyard/parlapi",
    packages=['parlapi'],
    long_description=read('README.md'),
    install_requires=[
        'beautifulsoup4>=4.4,<5',
        'cffi>=1.8,<2',
        'click>=6.6,<7',
        'dateparser>=0.4,<0.5',
        'flask>=0.11,<0.12',
        'flask-graphql>=1.3,<2',
        'flask-marshmallow>=0.7,<0.8',
        'flask-sqlalchemy>=2.1,<3',
        'graphene_sqlalchemy>=1.0,<2',
        'html5lib>=0.9999999,<1',
        'humanize>=0.5,<1',
        'ijson>=2.3,<3',
        'marshmallow-sqlalchemy>=0.10,<0.11',
        'psycopg2>=2,<3',
        'pycparser==2.13',  # 2.14 has CFFI bug
        'requests>=2.10,<3',
        'sqlalchemy-searchable>=0.10,<1',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
    ],
    entry_points='''
        [console_scripts]
        parlapi=parlapi.cli:cli
    '''
)
