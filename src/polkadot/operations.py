import functools
import os
import pygit2
import requests
import shutil
import traceback

from polkadot.globber import glob
from polkadot.logging import logger, log_operation


def filer(fn):
    @functools.wraps(fn)
    def inner(path, *args, deps = None, **kwargs):
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
    logger.debug("touch %s" % dest)
    yield open(dest, 'a').close()
    yield os.utime(dest, None)

@filer
def mkdir(dest, config = None):
    logger.debug("mkdir %s" % dest)
    yield os.makedirs(dest, exist_ok = True)

@filer
def mode(dest, octal, config = None):
    logger.debug("chmod %s %s" % (dest, oct(octal)))
    yield os.chmod(dest, octal)

@filer
def gitclone(dest, source, branch = 'master', config = None):
    logger.debug("git clone %s into %s on '%s'" % (source, dest, branch))
    try:
        yield pygit2.clone_repository(source, dest, checkout_branch = branch)
    except ValueError:
        logger.info("skipped git clone for existing repository in %s" % (dest))
        yield None

@filer
def download(dest, source, config = None):
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

