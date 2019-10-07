import sshCommand
import parse_logs
import pprint
import syncBashScripts
from . import archive_logs
from . import list_logs
from . import build_rerun
from . import error_check
from . import see_errors

PYTHON_PATH = "/home/users/jeffderb/python3/bin/python3 "
SCRIPT_DIR = "/root/migrate_helper_scripts/"


def too_many_logs(server, too_many_list, counter):
    f = open("migrate_errors/" + server + ".log", "w+")
    for volume, message in counter:
        if counter[(volume, message)] > 2:
            f.write("Volume: " + volume + " Message snippet: " + message + " Count: "
                    + str(counter[(volume, message)]) + "\n")
    f.close()
    syncBashScripts.rsync(server, "migrate_errors")
    process(server, "mail", " '" + '|'.join(too_many_list) + "'")


def print_logs(server, item, output):
    print(server)
    print(item)
    if len(output.stderr) > 0:
        print("Error")
        print(output.stderr.decode())
    elif len(output.stdout) > 0:
        print("Success")
        if item == "see_errors":
            archive, rerun, too_many, counter = parse_logs.parse_logs(server, output.stdout.decode())
            print("archive: " + str(len(archive)))
            print("rerun: " + str(len(rerun)))
            print("too many: " + str(len(too_many)))
            if len(archive) > 0:
                pprint.pprint(archive)
                archive_count = archive_logs.archive("archive-with-errors", sorted(archive))
                pprint.pprint(list_logs.get_logs('archive-with-errors', sorted(archive)))
                print("Archive")
                pprint.pprint(archive_count, indent=1)
            if len(rerun) > 0:
                rerun_logs = build_rerun.rerun(rerun)
                print("Rerun")
                pprint.pprint(rerun_logs, indent=1)
            if len(too_many) > 0:
                print("More than 2 errors:")
                pprint.pprint(too_many, indent=1)
                pprint.pprint(counter, indent=1)
                too_many_logs(server, sorted(too_many), counter)

        else:
            print(output.stdout.decode())
    else:
        print("No output at this time.")
    print("End of output")


def process(server, item, volume=False):

    if item == "check":
        output = error_check.main()

    elif item == "rerun":
        if volume:
            command = "bash /root/migrate_helper_scripts/rerunMigrationErrors.sh " + volume
        else:
            command = "bash /root/migrate_helper_scripts/rerunMigrationErrors.sh"

    elif item == "archive" or item == "archive_with_errors":
        output = archive_logs.archive(item, volume)

    elif item == "fix_archives":
        command = "bash /root/migrate_helper_scripts/fixArchives.sh"

    elif item == "group_errors":
        command = "bash /root/migrate_helper_scripts/groupErrorsByExperiments.sh"

    elif item == "see_errors":
        output = see_errors.see_errors()
        archive, rerun, too_many, counter = parse_logs.parse_logs(server, output)
        print("archive: " + str(len(archive)))
        print("rerun: " + str(len(rerun)))
        print("too many: " + str(len(too_many)))
        if len(archive) > 0:
            pprint.pprint(archive)
            archive_count = archive_logs.archive("archive-with-errors", sorted(archive))
            pprint.pprint(list_logs.get_logs('archive-with-errors', sorted(archive)))
            print("Archive")
            pprint.pprint(archive_count, indent=1)
        if len(rerun) > 0:
            rerun_logs = build_rerun.rerun(rerun)
            print("Rerun")
            pprint.pprint(rerun_logs, indent=1)
        if len(too_many) > 0:
            print("More than 2 errors:")
            pprint.pprint(too_many, indent=1)
            pprint.pprint(counter, indent=1)
            too_many_logs(server, sorted(too_many), counter)

    elif item == "mail":
        command = "bash /root/migrate_helper_scripts/mailErrors.sh " + volume

    else:
        command = "echo 'do nothing'"

    print(server)
    print(item)
    pprint.pprint(output, indent=4)

    _errors(server, item, output)


def _errors(server, item, output):
    # output = sshCommand.sshcmd(server, command)
    # print(output.stdout.decode())
    print_logs(server, item, output)
