import subprocess


def main():
    volumes_running = []
    process = subprocess.run(['ps', 'waux'], capture_output=True)
    volumes_running = process.stdout

    return volumes_running


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
