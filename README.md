# polkadot

polkadot is a Linux dotfiles manager written in Python. It supports templating through Jinja2 and uses Git for source control.

## requirements

1. a recent version of libgit2 (>=0.26.0) to provide git2.h to pygit2
2. Python 3.5 or higher for fancy syntax

## usage

polkadot is configured using Python source code (think Django's `settings.py`).

all names in your source code that are uppercase and do not start with an underscore will be added to the template context.

to use the polkadot module from the command line,

```
python -m polkadot.dance polkadot.py
```

to run polkadot without making any changes you can use the `--dry-run` option:
```
python -m polkadot.dance polkadot.py --dry-run
```

to pass additional configuration options at run time, you can pass multiple `--extra` options:
```
python -m polkadot.dance polkadot.py --extra PATH=$PATH:$HOME/bin --extra FOO=BAR
```


## extending functionality

polkadot provides a lightweight wrapper around typical system utilities in the `os` and `shutil` modules.
if you need additional functionality such as creating a pipe or cloning a subversion repository,
write a generator that performs your functionality and and decorate it with the `polkadot.operations.filer` decorator.
at a minimum your function must accept a single positional argument and a single keyword argument `config`.
