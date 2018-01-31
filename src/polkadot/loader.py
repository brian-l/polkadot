import os

from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader

from jinja2 import Environment, FileSystemLoader

from polkadot.logging import logger


REQUIRED_ATTRIBUTES = {
    'DOTFILES',
}


def load_config(path, dry_run, extras):
    """
    load a source file into a dictionary keeping only names that are uppercase and don't start with _

    provides some default/initial options and handles missing options.

    :param str path: path to the configuration file
    :param bool dry_run: if True don't make changes
    :param dict extras: optional extra arguments and options
    """
    src = SourceFileLoader('polkadot.config', path)
    spec = spec_from_loader('polkadot.config', src)
    mod = module_from_spec(spec)

    try:
        spec.loader.exec_module(mod)
    except FileNotFoundError:
        logger.error("Couldn't open configuration file: %s" % (path,))
        return

    config = {
        'DOTFILES_DRY_RUN': dry_run,
        'DOTFILES_HOME_DIRECTORY': os.getenv('HOME'),
        'DOTFILES_WORKING_DIRECTORY': os.path.dirname(os.path.abspath(path)),
        'DOTFILES_JINJA_ENV': Environment(
            loader = FileSystemLoader('./'),
        )
    }
    for attr in dir(mod):
        if not attr.startswith('_') and attr == attr.upper():
            config[attr] = getattr(mod, attr)

    missing  = REQUIRED_ATTRIBUTES.difference(config.keys())
    if missing:
        for attr in sorted(missing):
            logger.error("Expected config file to define %s." % attr)
        return
    else:
        yield from execute_config({**config, **extras})

def execute_config(config):
    """
    run through each generator and evaluate the file changes

    :param dict config: dictionary form of the configuration file combined with extra arguments and options
    """
    for dotfile in config['DOTFILES']:
        files = iter(dotfile)
        next(files)
        files.send(config)
        yield from files



