import logging


logger = logging.getLogger('polkadot')
if not logger.handlers:
    logging.basicConfig(level = logging.WARNING)

def log_operation(fn, path, fnargs, fnkwargs):
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
