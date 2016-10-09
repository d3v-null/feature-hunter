# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    package_license = f.read()

setup(
    name='feature_hunter',
    version='0.0.1',
    description='A python module for trawling music websites that detects changes in lists of feature albums and sends notifications by email',
    long_description=readme,
    author='Derwent McElhinney',
    author_email='derwent@laserphile.com',
    url='https://github.com/derwentx/feature-hunter',
    license=package_license,
    packages=find_packages(exclude=('tests', 'docs'))
)
