#!/home/users/jeffderb/python3/bin/python3


import list_logs as list_logs
import pprint
import re


MIGRATION_DIR = "/var/migration/"


def see_errors():
    error_files = list_logs.get_logs("errors")
    all_errors = []
    for file in error_files:
        file_name = MIGRATION_DIR + file
        with open(file_name, 'rb') as fh:
            error_message = ""
            first = next(fh).decode().split()
            volume = first[-1]
            for line in fh.readlines():
                message = line.decode()
                if re.search('ERR', message):
                    error_message = message
                    break
        error = volume + " ---- " + file_name + " ---- " + error_message
        print(error)
        all_errors.append(error)

    # pprint.pprint(all_errors)

    return all_errors


if __name__ == '__main__':
    see_errors()
