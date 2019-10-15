import sh


def main():
    volumes_running = []
    process = sh.grep(sh.ps('ww'), 'migrate_chimera')

    return process


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
