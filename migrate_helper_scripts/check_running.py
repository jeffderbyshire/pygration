import subprocess


def main():
    volumes_running = []
    process = subprocess.run(['/var/migration/migration-bin/dmPs.sh'], check=True,
                             shell=True, stdout=subprocess.PIPE, universal_newlines=True)

    return process.stdout


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
