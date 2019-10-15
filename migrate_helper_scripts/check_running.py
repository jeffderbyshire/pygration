import sh


def main():
    volumes_running = []
    process = sh.grep(sh.ps('ww'), 'migrate_chimera')
    for line in process:
        print(line)

    return process


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
