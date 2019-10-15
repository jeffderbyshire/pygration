from subprocess import Popen, PIPE


def main():
    volumes_running = []
    process_ps = Popen(['ps', 'w'], check=True,
                    stdout=PIPE, text=True)
    process_grep = Popen(['grep', 'migrate_chimera'], stdin=process_ps.stdout, stdout=PIPE)

    return process_grep.stdout


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
