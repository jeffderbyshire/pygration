import sshCommand
import parse_logs
import pprint
import syncBashScripts
import archive_logs as archive_logs
import list_logs as list_logs

PYTHON_PATH = "/home/users/jeffderb/python3/bin/python3 "
SCRIPT_DIR = "/root/migrate_helper_scripts/"


def rerun_logs(server, rerun_list):
    process(server, "rerun", " '" + '|'.join(rerun_list) + "'")


def too_many_logs(server, too_many_list, counter):
    f = open("migrate_errors/" + server + ".log", "w+")
    for volume, message in counter:
        if counter[(volume, message)] > 2:
            f.write("Volume: " + volume + " Message snippet: " + message + " Count: "
                    + str(counter[(volume, message)]) + "\n")
    f.close()
    syncBashScripts.rsync(server, "migrate_errors")
    process(server, "mail", " '" + '|'.join(too_many_list) + "'")


def print_logs(server, item, command, output):
    print(server)
    print(item)
    print(command)
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
                archive_count = archive_logs.archive("archive-with-errors", sorted(archive))
                pprint.pprint(list_logs.get_logs('archive-with-errors', sorted(archive)))
                print("Archive")
                pprint.pprint(archive_count, indent=1)
            if len(rerun) > 0:
                rerun_logs(server, sorted(rerun))
                print("Rerun")
                pprint.pprint(rerun, indent=1)
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
        command = PYTHON_PATH + SCRIPT_DIR + "error_check.py "

    elif item == "rerun":
        if volume:
            command = "bash /root/migrate_helper_scripts/rerunMigrationErrors.sh " + volume
        else:
            command = "bash /root/migrate_helper_scripts/rerunMigrationErrors.sh"

    elif item == "archive" or item == "archive_with_errors":
        if volume:
            command = PYTHON_PATH + SCRIPT_DIR + "archive_logs.py " + item + volume
        else:
            command = PYTHON_PATH + SCRIPT_DIR + "archive_logs.py "

    elif item == "fix_archives":
        command = "bash /root/migrate_helper_scripts/fixArchives.sh"

    elif item == "group_errors":
        command = "bash /root/migrate_helper_scripts/groupErrorsByExperiments.sh"

    elif item == "see_errors":
        command = PYTHON_PATH + SCRIPT_DIR + "see_errors.py "

    elif item == "mail":
        command = "bash /root/migrate_helper_scripts/mailErrors.sh " + volume

    else:
        command = "echo 'do nothing'"

    _errors(server, item, command)


def _errors(server, item, command):
    output = sshCommand.sshcmd(server, command)
    # print(output.stdout.decode())
    print_logs(server, item, command, output)
