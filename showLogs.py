import sshCommand
from migrate_helper_scripts.migrationLogs import print_logs


PYTHON_PATH = "/home/users/jeffderb/python3/bin/python3 "
SCRIPT_DIR = "/root/migrate_helper_scripts/"


def migration_logs(server: str, arg: str):
    """ connect to server and run rsync'ed bash script with arg """
    command = PYTHON_PATH + SCRIPT_DIR + "list_logs.py " + arg
    output = sshCommand.sshcmd(server, command)
    print_logs(server, "Logs", command, output)
