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
        'click>=6.6,<7',
        'flask>=0.11,<0.12',
        'flask-sqlalchemy>=2.1,<3',
        'html5lib>=0.9999999,<1',
        'ijson>=2.3,<3',
        'requests>=2.10,<3'
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
