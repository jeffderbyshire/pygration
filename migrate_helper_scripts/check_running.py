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
    print(processes.stdout.decode())
    print(processes.stderr.decode())
    exit()
    results = [line.strip() for line in processes.stdout.decode()]
    for process in results:
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
