""" check running migration processes """

from configparser import ConfigParser
import sh

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

    return volumes_running


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
