#!/usr/bin/env python
# -*- coding: utf-8 -*-

with open('README.rst') as readme:
    __doc__ = readme.read()

from setuptools import setup

setup(
    name='pymips',
    version='0.2',
    description=u'A MIPS processor implemented with Python',
    long_description=__doc__,
    author = u'Martín Gaitán',
    author_email = 'gaitan@gmail.com',
    url='https://github.com/nqnwebs/pymips',
    packages=['pymips'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Topic :: System :: Hardware'
      ]
)
