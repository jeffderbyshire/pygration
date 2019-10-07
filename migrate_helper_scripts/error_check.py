#!/home/users/jeffderb/python3/bin/python3

from . import list_logs
import os

MIGRATION_DIR = "/var/migration/"


def main():
    output_renames = {}
    unchecked_files = list_logs.get_logs("no-errors")
    for file in unchecked_files:
        file_name = MIGRATION_DIR + file
        output_renames[file_name] = ''
        error = ".0"
        with open(file_name, 'rb') as fh:
            first = next(fh).decode().split()
            volume = first[-1]
            if os.path.getsize(file_name) > 1024:
                file_size = 1024
            else:
                file_size = int(os.path.getsize(file_name))
            fh.seek(-1 * file_size, 2)
            last = fh.readlines()[-1].decode().split()
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


