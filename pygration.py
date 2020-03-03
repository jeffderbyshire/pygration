""" pygration doc string

This program is created to help build automation for tape migration.

"""
import logging
import pprint
import socket
from configparser import ConfigParser
import click
import migrate_helper_scripts.migration_logs as migration_logs
import migrate_helper_scripts.list_logs as list_logs
import migrate_helper_scripts.error_check as error_check
import migrate_helper_scripts.migration_status as migration_status
import migrate_helper_scripts.fix_archives as fix_archives
import migrate_helper_scripts.unity as unity
import migrate_helper_scripts.build_scan as build_scan

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
LOG_DIR = CONFIG['Default']['log_dir']
DEBUG = True

logging.basicConfig(filename=LOG_DIR + "/reruns/migration.log",
                    format='%(asctime)s %(levelname)s:%(message)s',
                    level=logging.INFO)


@click.command()
@click.option('--logs', type=click.Choice(['all', 'errors', 'no-errors', 'archive',
                                           'archive-with-errors']))
@click.option('--process', type=click.Choice(['all', 'fix', 'status', 'import']))
@click.option('--quiet', is_flag=True)
@click.option('--check', is_flag=True)
@click.option('--scan', nargs=1)
def main(logs, process, quiet, check, scan):
    """ Parse command arguments, build server list and run commands """
    server = socket.gethostname()

    if logs:
        pprint.pprint(list_logs.get_logs(logs))

    if process in ['all', 'fix', 'status']:
        migration_status.report_status()
        if process == 'fix':
            fix_archives.main()
            migration_status.report_status()
        elif process == 'all':
            migration_logs.process(server=server, quiet=quiet, rerun=True)
            migration_status.report_status()

    if process in ['import']:
        unity.db_import()

    if scan:
        if not DEBUG:
            unity.db_import()
        build_scan.scan(scan)

    if check:
        output = error_check.main()
        if not quiet:
            pprint.pprint(output, indent=4)


main()

exit()
