import subprocess


def main():
    volumes_running = []
    process = subprocess.run(['ps', '-aux'], check=True,
                             stdout=subprocess.PIPE, text=True)

    return process.stdout.split('\n')


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
