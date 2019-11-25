""" Setup personal packages for import statements """
from setuptools import setup, find_packages

setup(
    name='migrate_helper',
    version='1.1',
    description='Migration Helpers',
    long_description='Check Logs for errors, Archive Logs, Parse logs, store errors, and rerun',
    author='Jeff Derbyshire',
    author_email='jeffderb@fnal.gov',
    url='https://hepcloud-git.fnal.gov:8443/jeffderb/migration-helper',
    packages=find_packages(exclude=('tests', 'config', 'db', 'build', 'dist')),
    install_requires=['sh', 'sqlalchemy', 'tqdm']
)
