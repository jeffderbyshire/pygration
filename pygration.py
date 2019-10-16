#!/home/users/jeffderb/python3/bin/python3
""" pygration doc string

This program is created to help build automation for tape migration.

Currently, it's a collection of bash scripts with some Python wrapping.  The scripts are uploaded
via rsync and run via ssh and python subprocess.

TODO: add command line arguments
pygration --server fdm1802 OR omit and parse all servers
pygration logs --no-errors: show logs without errors
pygration logs --errors:    show logs with errors
pygration logs --all:       show all logs
pygration process check:    check logs for errors and rename
pygration process rerun:    build rerun script based on errors TODO: more complete error checking
pygration process archive:  archive processed logs to 'yyyy/mm' folder

Examples: pygration logs --no-errors process check --server fdm1802


TODO: figure out how to use classes / split into modules

"""
import argparse
import textwrap
import socket
from migrate_helper_scripts import migrationLogs
from migrate_helper_scripts import list_logs
import pprint


def build_migration_node_list():
    """ built migration node and return list of nodes
    Luckily the nodes are in numbered sequentially
    TODO: replace with external configure file
    """
    server_prefix: str = "fdm18"
    servers = []
    for number in range(1, 9):
        # servers fdm1801..08
        servers.append(server_prefix+"{0:02d}".format(number))

    server_prefix: str = "stkendm"
    server_postfix: str = "a"
    for number in range(1, 3):
        # servers stkendm01..02a
        servers.append(server_prefix+"{0:02d}".format(number)+server_postfix)

    return servers


def get_args() -> argparse:
    """ Parse command line arguments and return object"""
    parser = argparse.ArgumentParser(description='Process Migration Logs',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--logs', metavar='log_type', nargs=1, default=False,
                        help=textwrap.dedent('''\
                            no-errors:    list logs without errors
                            errors:       show logs with errors
                            all:          show all logs
                            default:        --all
                            '''))
    parser.add_argument('--process', metavar='action', nargs=1, default=False,
                        help=textwrap.dedent('''\
                            check:              look for errors and rename logs
                            rerun:              build rerun script and run inside screen
                            archive:            archive old logs into year / month folders
                            archive_with_errors:archive old (> 2 days) into folders  
                            fix_archives:       fix log names in archived log folders
                            group_errors:       put log files into files with experiments
                            get_volume_serial:  get volume serials
                            default:            do nothing
                            '''))
    parser.add_argument('--server', dest='server', metavar='node', nargs=1, default='all',
                        help='run command(s) on single node')
    parser.add_argument('--quiet', action='store_true',
                        help='suppress output for cron job')
    parser.add_argument('--volumes', metavar='volume_serials', nargs='+', default=False,
                        help='volume serials [ VPXXXX1 VPXXXX2 ... VPXXXXN ]')

    return parser.parse_args()


def main():
    """ Parse command arguments, build server list and run commands """
    args = get_args()
    server = socket.gethostname()
    if args.logs:
        pprint.pprint(list_logs.get_logs(args.logs[0]))
    if args.process:
        migrationLogs.process(server=server, item=args.process[0], quiet=args.quiet)
    """    
    # if args.server == 'all':  # default
        # servers = socket.gethostname()
        # servers = build_migration_node_list()
    # else:
        servers = args.server
    # for server in servers:
        # syncBashScripts.rsync(server, "migrate_helper_scripts")
    pprint.pprint(list_logs.get_logs(args.logs[0]))
        # showLogs.migration_logs(server, args.logs[0])
    """


main()

# log error messages
# MIGRATING_VOLUME do not set VOV869 to migrated due to previous error


exit()
