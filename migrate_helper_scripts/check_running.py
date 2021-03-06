""" check running migration processes """

from configparser import ConfigParser
import socket
import subprocess
import logging
import migrate_helper_scripts.database_schema as database

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
RUNNING = CONFIG['Process']['running']
DEBUG = False


def main():
    """
    :return: volume serials if other migrate_chimera process found
    """
    volumes_running = []
    process_running = []
    processes = subprocess.run(
        [
            'ps',
            'ww'
        ],
        capture_output=True,
    )
    for process in processes.stdout.decode().split('\n'):
        if RUNNING in process:
            if DEBUG:
                logging.info("%s", process.split())
            try:
                volumes_running.append(process.split()[-1])
                process_running.append(process.split()[0])
            except IndexError:
                pass

    if volumes_running:
        database.update_running(socket.gethostname(), volumes_running)

    return volumes_running, process_running


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
