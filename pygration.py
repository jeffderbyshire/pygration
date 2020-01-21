""" pygration doc string

This program is created to help build automation for tape migration.

"""
import pprint
import socket
import click

import migrate_helper_scripts.migration_logs as migration_logs
import migrate_helper_scripts.list_logs as list_logs
import migrate_helper_scripts.error_check as error_check
import migrate_helper_scripts.migration_status as migration_status
import migrate_helper_scripts.fix_archives as fix_archives


@click.command()
@click.option('--logs', type=click.Choice(['all', 'errors', 'no-errors', 'archive',
                                           'archive-with-errors']))
@click.option('--process', type=click.Choice(['all', 'fix', 'status']), default='all')
@click.option('--quiet', is_flag=True)
@click.option('--check', is_flag=True)
def main(logs, process, quiet, check):
    """ Parse command arguments, build server list and run commands """
    server = socket.gethostname()

    if logs:
        pprint.pprint(list_logs.get_logs(logs))
    print(process)
    if process in ['all', 'fix', 'status']:
        migration_status.report_status()
        if process == 'fix':
            fix_archives.main()
        elif process == 'status':
            migration_status.report_status()
        else:
            migration_logs.process(server=server, quiet=quiet, rerun=False)

    if check:
        output = error_check.main()
        if not quiet:
            pprint.pprint(output, indent=4)


main()


exit()
