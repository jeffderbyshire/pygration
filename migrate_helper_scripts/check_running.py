import subprocess


def main():
    volumes_running = []
    with subprocess.Popen(["ps ww |grep migrate_chimera"],
                          stdout=subprocess.PIPE) as proc:
        volumes_running.append(proc.stdout.read())

    return volumes_running


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
