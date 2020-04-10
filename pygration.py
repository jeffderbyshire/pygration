""" pygration doc string

This program is created to help build automation for tape migration.

"""
import logging
import logging.handlers
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
import migrate_helper_scripts.clean_spool as clean_spool

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
LOG_DIR = CONFIG['Default']['log_dir']

HANDLER = logging.handlers.TimedRotatingFileHandler(LOG_DIR + "/reruns/migration.log",
                                                    when='W0',
                                                    backupCount=7)
HANDLER.setLevel(logging.INFO)
HANDLER.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:%(message)s'))
logging.basicConfig(handlers=HANDLER)


@click.command()
@click.option('--logs', type=click.Choice(['all', 'errors', 'no-errors', 'archive',
                                           'archive-with-errors']))
@click.option('--process', type=click.Choice(['all', 'fix', 'spool', 'status', 'import']))
@click.option('--quiet', is_flag=True)
@click.option('--check', is_flag=True)
@click.option('--scan', nargs=1)
def main(logs, process, quiet, check, scan):
    """ Parse command arguments, build server list and run commands """
    server = socket.gethostname()

    if logs:
        pprint.pprint(list_logs.get_logs(logs))

    if process in ['all', 'fix', 'spool', 'status']:
        if not quiet:
            migration_status.report_status()
        if process == 'fix':
            fix_archives.main()
        elif process == 'spool':
            clean_spool.clean(quiet)
        elif process == 'all':
            migration_logs.process(server=server, quiet=quiet, rerun=True)
            clean_spool.clean(quiet)
        if not quiet:
            migration_status.report_status()

    if process in ['import']:
        unity.db_import(quiet)

    if scan:
        build_scan.scan(scan)

    if check:
        output = error_check.main()
        if not quiet:
            pprint.pprint(output, indent=4)


main()

exit()
