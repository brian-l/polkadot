import os

from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader

from jinja2 import Environment, FileSystemLoader

from polkadot.logging import logger


REQUIRED_ATTRIBUTES = {
    'DOTFILES', 'DOTFILES_GIT_REPOSITORY',
}


def load_config(path, dry_run, extras):
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
    for dotfile in config['DOTFILES']:
        files = iter(dotfile)
        next(files)
        files.send(config)
        yield from files



