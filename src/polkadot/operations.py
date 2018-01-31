import functools
import os
import pygit2
import shutil

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
    logger.debug("copy %s to %s" % (source, dest))
    if template:
        template = config['DOTFILES_JINJA_ENV'].get_template(source)
        output = template.render(config)
        with open(dest, 'w') as d:
            d.write(output)
        yield shutil.copystat(source, dest)
    else:
        yield shutil.copy2(source, dest)

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
    yield pygit2.clone_repository(source, dest, checkout_branch = branch)

