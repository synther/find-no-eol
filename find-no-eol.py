import argparse
import os
import fnmatch
import sys


class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


class FindNoEol:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--ignore-dir', action='append', default=[])
        parser.add_argument('--scan-pattern', action='append', default=[])
        parser.add_argument('--short', action='store_true')
        parser.add_argument('path', nargs='*', default='.')
        args = parser.parse_args()

        self.ignore_dirs = [os.path.abspath(d) for d in args.ignore_dir]
        self.scan_dirs = [os.path.abspath(d) for d in args.path]
        self.scan_patterns = args.scan_pattern
        self.short_output = args.short
        self.is_any_failed = False

    def print_args(self):
        print(Color.BOLD + 'Dirs to scan:' + Color.END)

        for d in self.scan_dirs:
            print(' - ' + d)

        print()

        if self.ignore_dirs:
            print(Color.BOLD + "Ignore dirs:" + Color.END)

            for d in self.ignore_dirs:
                print(' - ' + d)

            print()

        if self.scan_patterns:
            print(Color.BOLD + "Scan ONLY these files:" + Color.END)

            for p in self.scan_patterns:
                print(' - ' + p)

            print()

    def test_eol(self, file_path):
        with open(file_path, 'r', newline=None) as f:
            f.seek(0, 2)
            file_len = f.tell()

            if file_len < 1:
                return True

            f.seek(file_len - 1, 0)
            return f.read() == '\n'

    def print_failed_file(self, file_path):
        if not self.is_any_failed:
            if not self.short_output:
                print(Color.BOLD + "No EOL:" + Color.END)

            self.is_any_failed = True

        if not self.short_output:
            print(Color.RED + ' - ' + Color.END + file_path)
        else:
            print(file_path)

    def scan_dir(self, path):
        for dirpath, _, files in os.walk(path):
            if any(dirpath.startswith(d) for d in self.ignore_dirs):
                continue

            for file_name in files:
                if self.scan_patterns:
                    if all(not fnmatch.fnmatch(file_name, pat) for pat in self.scan_patterns):
                        continue

                full_path = os.path.join(dirpath, file_name)

                try:
                    if not self.test_eol(full_path):
                        self.print_failed_file(full_path)
                except Exception:
                    print("Error on file {}".format(
                        full_path), file=sys.stderr)
                    # raise

    def run(self):
        if not self.short_output:
            self.print_args()

        for path in self.scan_dirs:
            self.scan_dir(os.path.abspath(path))

        if not self.is_any_failed:
            print(Color.GREEN + Color.BOLD + "All files have EOL" + Color.END)


if __name__ == "__main__":
    FindNoEol().run()
