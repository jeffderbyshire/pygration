""" reports """

import os
from configparser import ConfigParser
from jinja2 import Environment, FileSystemLoader, select_autoescape
import migrate_helper_scripts.database_schema as database

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
REPORT = CONFIG['Reports']['migration_report']


def migration():
    """ migration report """
    env = Environment(
        loader=FileSystemLoader(os.getcwd() + '/templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('migration_report.html')
    with open(REPORT, "w") as file:
        file.write(template.render(result=database.get_migration_state_report()))
