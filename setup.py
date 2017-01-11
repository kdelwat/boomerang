#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'sanic',
    'aiohttp'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='boomerang',
    version='0.6.0',
    description="An asynchronous Python library for building services on the Facebook Messenger Platform",
    long_description=readme + '\n\n' + history,
    author="Cadel Watson",
    author_email='cadel@cadelwatson.com',
    url='https://github.com/kdelwat/boomerang',
    packages=[
        'boomerang',
    ],
    package_dir={'boomerang':
                 'boomerang'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='boomerang',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
