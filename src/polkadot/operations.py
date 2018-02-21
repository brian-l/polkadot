import functools
import os
import requests
import shutil
import traceback

from git import Repo
from git.exc import GitCommandError

from polkadot.globber import glob
from polkadot.logging import logger, log_operation


def filer(fn):
    """
    decorator that makes file operations lazy and builds a dependency tree.
    functions decorated with this generator must always yield, even in the case of failure.

    :param fn: function performing some side effect
    """
    @functools.wraps(fn)
    def inner(path, *args, deps = None, **kwargs):
        """
        generator wrapper that receives the polkadot config as the ``DOTFILES`` are iterated.

        if relative paths are provided in ``path``, it is assumed that the home directory is where the files are being added.

        .. note:: if a generator fails to yield, the whole pipeline will stop.

        :param str path: required part of the destination file:
        :param tupls args: optional positional arguments
        :param list deps: nested dependencies, e.g. mkdir before touching a file
        :param dict kwargs: optional keyword arguments which allow for support of different operations
        """
        config = (yield)

        if deps:
            for dep in deps:
                yield from dep

        if not path.startswith('/'):
            path = os.path.join(config['DOTFILES_HOME_DIRECTORY'], path)

        if config['DOTFILES_DRY_RUN']:
            yield log_operation(fn, path, args, kwargs)
        else:
            yield from fn(path, *args, config = config, **kwargs)

    return inner

@filer
def copy(dest, source, config = None, template = True):
    """
    open a file, template it, write the rendered output to the destination and set file metadata

    .. note:: accepts wildcards for both arguments

    :param str dest: string or wildcard pattern for destination file(s)
    :param str source: string or wildcard pattern for source file(s)
    :param bool template: if False, skip jinja templating
    :param dict config: polkadot config dictionary
    """
    sources = list(glob(source, config['DOTFILES_WORKING_DIRECTORY']))

    if source.endswith('*') and not dest.endswith('*'):
        logger.error("Globbed sources must be copied to a globbed directory.")
        return
    else:
        dest = os.path.dirname(dest)

    for source in sources:
        realdest = os.path.join(dest, os.path.basename(source))
        logger.debug("copy %s to %s" % (source, realdest))

        if template:
            template = config['DOTFILES_JINJA_ENV'].get_template(source)
            output = template.render(config)
            with open(realdest, 'w') as d:
                d.write(output)
            yield shutil.copystat(source, realdest)
        else:
            yield shutil.copy2(source, realdest)

@filer
def touch(dest, config = None):
    """
    touch a file, creating if it doesn't exist and setting the access time.

    :param str dest: string or wildcard pattern for destination file
    :param dict config: polkadot config dictionary
    """
    logger.debug("touch %s" % dest)
    yield open(dest, 'a').close()
    yield os.utime(dest, None)

@filer
def mkdir(dest, config = None):
    """
    make a directory like ``mkdir -p``

    :param str dest: string or wildcard pattern for destination directory
    :param dict config: polkadot config dictionary
    """
    logger.debug("mkdir %s" % dest)
    yield os.makedirs(dest, exist_ok = True)

@filer
def mode(dest, octal, config = None):
    """
    set a file mode on ``dest``

    :param str dest: string or wildcard pattern for destination file
    :param int octal: octal representation (0o744) for chmod
    :param dict config: polkadot config dictionary
    """
    logger.debug("chmod %s %s" % (dest, oct(octal)))
    yield os.chmod(dest, octal)

@filer
def gitclone(dest, source, branch = 'master', config = None, git_kwargs = None):
    """
    clone a git repository

    .. note:: this will skip the repo if it already exists, it will not run ``git pull``

    :param str dest: string or wildcard pattern for destination directory
    :param str source: git url for source repository
    :param str branch: branch to check out when repository is cloned
    :param dict config: polkadot config dictionary
    """
    logger.debug("git clone %s into %s on '%s'" % (source, dest, branch))
    try:
        yield Repo().clone_from(
            source, dest,
            branch = branch,
            **(git_kwargs or {})
        )
    except GitCommandError:
        logger.debug(traceback.format_exc())
        logger.info("skipped git clone for existing repository in %s" % (dest))
        yield None

@filer
def download(dest, source, config = None):
    """
    streams a file using requests

    :param str dest: string or destination file
    :param str source: remote url for source file
    :param dict config: polkadot config dictionary
    """
    logger.debug("downloading file from %s into %s" % (source, dest))
    try:
        request = requests.get(source, stream = True)
        with open(dest, 'wb') as output:
            for chunk in request.iter_content(chunk_size = 1024):
                if chunk:
                    yield output.write(chunk)
    except:
        logger.error('failed to download file')
        logger.error(traceback.format_exc())
        yield None

