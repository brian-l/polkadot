import fnmatch
import os


def glob(path, base):
    for root, dirs, files in os.walk(base):
        for fname in files:
            full = os.path.normpath(os.path.join(root, fname).replace(base, '.'))
            if fnmatch.fnmatch(full, path):
                yield full

