""" reports """

import os
from datetime import datetime
from configparser import ConfigParser
from jinja2 import Environment, FileSystemLoader, select_autoescape
import migrate_helper_scripts.database_schema as database

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
REPORT = CONFIG['Reports']['migration_report']


def migration():
    """ migration report """
    navigation = {
        '1_url': CONFIG['Reports']['1_url'],
        '1_text': CONFIG['Reports']['1_text'],
        '2_url': CONFIG['Reports']['2_url'],
        '2_text': CONFIG['Reports']['2_text'],
        'dropdown_text': CONFIG['Reports']['dropdown_text'],
        'dropdown_1_url': CONFIG['Reports']['dropdown_1_url'],
        'dropdown_1_text': CONFIG['Reports']['dropdown_1_text'],
        'dropdown_2_url': CONFIG['Reports']['dropdown_2_url'],
        'dropdown_2_text': CONFIG['Reports']['dropdown_2_text'],
    }
    env = Environment(
        loader=FileSystemLoader(os.getcwd() + '/templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('migration_report.html')
    now = datetime.now()
    with open(REPORT, "w") as file:
        file.write(template.render(result=database.get_migration_state_report(),
                                   updated=now.strftime("%m/%d/%Y, %H:%M:%S"),
                                   report_name='Migration Completion Report',
                                   navigation=navigation))
