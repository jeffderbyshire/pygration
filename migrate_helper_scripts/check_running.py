""" check running migration processes """

from configparser import ConfigParser
import socket
import sh
import migrate_helper_scripts.database_schema as database

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
RUNNING = CONFIG['Process']['running']


def main():
    """
    :return: volume serials if other migrate_chimera process found
    """
    volumes_running = []
    try:
        process = sh.grep(sh.ps('ww'), RUNNING)
    except sh.ErrorReturnCode:
        return volumes_running
    for line in process:
        volumes_running.append(line.split()[-1])

    database.update_running(socket.gethostname(), volumes_running)

    return database.get_running()


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
