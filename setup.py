#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='ppp_logger',
    version='0.1',
    description='Logging backend for PPP user interfaces.',
    url='https://github.com/ProjetPP/PPP-Core',
    author='Valentin Lorentz',
    author_email='valentin.lorentz+ppp@ens-lyon.org',
    license='MIT',
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries',
    ],
    install_requires=[
        'requests',
        'sqlalchemy>=0.9',
        'ppp_datamodel>=0.5,<0.6',
        'ppp_core>=0.5,<0.6',
    ],
    packages=[
        'ppp_logger',
    ],
)


