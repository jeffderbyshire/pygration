import subprocess


def main():
    volumes_running = []
    process = subprocess.run(['ps', 'waux'], capture_output=True)
    for line in process.stdout:
        volumes_running.append(line)

    return volumes_running


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
