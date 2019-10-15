import subprocess


def main():
    volumes_running = []
    with subprocess.run(['ps', 'waux'], capture_output=True) as proc:
        volumes_running.append(proc.stdout)

    return volumes_running


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
