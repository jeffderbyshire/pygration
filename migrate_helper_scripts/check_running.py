""" check running migration processes """

from configparser import ConfigParser
import socket
import subprocess
import migrate_helper_scripts.database_schema as database

CONFIG = ConfigParser()
CONFIG.read('config/config.conf')
RUNNING = CONFIG['Process']['running']


def main():
    """
    :return: volume serials if other migrate_chimera process found
    """
    volumes_running = []
    processes = subprocess.run(
        [
            'ps',
            'ww'
        ],
        capture_output=True,
    )
    for process in processes.stdout.decode():
        print(process)
        exit()
        if RUNNING in process:
            try:
                volumes_running.append(process.split()[-1])
            except IndexError:
                pass

    if volumes_running:
        database.update_running(socket.gethostname(), volumes_running)

    return volumes_running


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
