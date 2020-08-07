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
        'url_one': CONFIG['Reports']['1_url'],
        'text_one': CONFIG['Reports']['1_text'],
        'url_two': CONFIG['Reports']['2_url'],
        'text_two': CONFIG['Reports']['2_text'],
        'dropdown_text': CONFIG['Reports']['dropdown_text'],
        'dropdown_a_url': CONFIG['Reports']['dropdown_1_url'],
        'dropdown_a_text': CONFIG['Reports']['dropdown_1_text'],
        'dropdown_b_url': CONFIG['Reports']['dropdown_2_url'],
        'dropdown_b_text': CONFIG['Reports']['dropdown_2_text'],
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
