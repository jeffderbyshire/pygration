import subprocess


def main():
    volumes_running = []
    with subprocess.Popen(['ps', 'waux'],
                          stdout=subprocess.PIPE) as proc:
        volumes_running = proc.stdout.readlines()

    return volumes_running


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
