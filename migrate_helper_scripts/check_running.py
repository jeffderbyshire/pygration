import subprocess


def main():
    volumes_running = []
    process = subprocess.run(['/var/migration/migration-bin/dmPs.sh'], capture_output=True)

    return process.stdout


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
