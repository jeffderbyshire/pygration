""" reports """

from jinja2 import Environment, FileSystemLoader, select_autoescape

import migrate_helper_scripts.database_schema as database


def migration():
    """ migration report """
    env = Environment(
        loader=FileSystemLoader('../templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('migration_report.html')
    result = database.get_migration_state_report()
    print(template.render(result))
