from subprocess import Popen, PIPE


def main():
    volumes_running = []
    process_ps = Popen(['ps', '-ww'],
                       stdout=PIPE)
    process_grep = Popen(['grep', 'migrate_chimera'], stdin=process_ps.stdout, stdout=PIPE)

    process_ps.stdout.close()  # Allow proc1 to receive a SIGPIPE if proc2 exits.
    out, err = process_grep.communicate()
    return out


if __name__ == "__main__":
    import pprint
    pprint.pprint(main())
