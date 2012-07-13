#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name='mongoscheduler',
    version='0.0.1',
    author='Brent Tubbs',
    author_email='brent.tubbs@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pymongo',
    ],
    url='http://bits.btubbs.com/celery-mongoscheduler',
    description='A Celery scheduler backend using MongoDB',
)
