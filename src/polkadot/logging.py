import logging


logger = logging.getLogger('polkadot')
if not logger.handlers:
    logging.basicConfig(level = logging.WARNING)

def log_operation(fn, path, fnargs, fnkwargs):
    """
    simple function that prints arguments passed into ``polkadot.operations.filer``

    :param fn: operation function that is decorated by filer
    :param path: path of the destination file
    :param fnargs: positional arguments passed to the decorated function
    :param fnkwargs: keyword arguments passed to the decorated function
    """
    params = ', '.join([
        *[repr(path)],
        *(repr(f) for f in fnargs),
        *['%s = %s' % (k, repr(v)) for k, v in fnkwargs.items()]
    ])

    logger.info(
        '%s.%s(%s)' % (
            fn.__module__,
            fn.__name__,
            params,
        )
    )
