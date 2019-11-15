""" check running migration processes """

import sh


def main():
    """
    :return: volume serials if other migrate_chimera process found
    """
    volumes_running = []
    try:
        process = sh.grep(sh.ps('ww'), 'migrate_chimera')
    except sh.ErrorReturnCode:
        return volumes_running
    for line in process:
        volumes_running.append(line.split()[-1])

    return volumes_running


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
