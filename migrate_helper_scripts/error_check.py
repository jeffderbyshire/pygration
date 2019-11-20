""" check log files for errors """

import os
import sys
import migrate_helper_scripts.list_logs as list_logs

MIGRATION_DIR = "/var/migration/"


def main():
    """ look for new log files and check for errors.  rename file with volume serial """
    output_renames = {}
    unchecked_files = list_logs.get_logs("no-errors")
    print(unchecked_files)
    sys.exit()
    for file in unchecked_files:
        file_name = MIGRATION_DIR + file
        output_renames[file_name] = ''
        error = ".0"
        with open(file_name, 'rb') as handle:
            first = next(handle).decode().split()
            volume = first[-1]
            if os.path.getsize(file_name) > 1024:
                file_size = 1024
            else:
                file_size = int(os.path.getsize(file_name))
            handle.seek(-1 * file_size, 2)
            last = handle.readlines()[-1].decode().split()
            if len(last) > 8:
                if (last[7] + last[8]) == "setcomment":
                    volume = volume
                else:
                    volume = volume + error
            else:
                volume = volume + error

        dst_file_name = file_name + "-" + volume
        os.rename(file_name, dst_file_name)
        output_renames[file_name] = dst_file_name

    return output_renames


if __name__ == '__main__':
    main()
