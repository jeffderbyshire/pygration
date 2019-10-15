import sh


def main():
    volumes_running = []
    process = sh.grep(sh.ps('ww'), 'migrate_chimera')
    for line in process:
        volumes_running.append(line.split()[-1])

    return volumes_running


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
