import fnmatch
import os


def glob(path, base):
    """
    glob.glob ignores hidden files. this one allows them, and matches against the relative path provided in the config.

    :param str path: string or wildcard that represents one or more files
    :param str base: base directory to run the relative path search in
    :returns: generator of filenames in the current directory that matched
    """
    for root, dirs, files in os.walk(base):
        for fname in files:
            full = os.path.normpath(os.path.join(root, fname).replace(base, '.'))
            if fnmatch.fnmatch(full, path):
                yield full

