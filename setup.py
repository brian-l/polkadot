#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'polkadot',
    version = '1.0.1',
    description = 'Python dotfiles manager',
    url = 'https://github.com/brian-l/polkadot',
    author = 'Brian Lee',
    author_email = 'brian-l@users.noreply.github.com',
    license = 'MIT',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    python_requires='>=3.5',
    zip_safe = False,
    install_requires = [
        'jinja2', 'GitPython', 'requests',
    ],
)
