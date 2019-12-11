""" Setup personal packages for import statements """
from setuptools import setup, find_packages

setup(
    name='pygration',
    version='3.1.0',
    py_modules=['pygration', 'migrate_helper_scripts'],
    description='Migration Helpers',
    long_description='Check Logs for errors, Archive Logs, Parse logs, store errors, and rerun',
    author='Jeff Derbyshire',
    author_email='jeffderb@fnal.gov',
    url='https://hepcloud-git.fnal.gov:8443/jeffderb/migration-helper',
    packages=find_packages(exclude=('tests', 'config', 'db', 'build', 'dist')),
    install_requires=['sh', 'sqlalchemy', 'tqdm', 'click']
)
