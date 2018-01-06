# -*- coding: utf-8 -*-
import codecs

from setuptools import setup


def get_version():
    with open('flake8_string_format.py') as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


def get_long_description():
    with codecs.open('README.rst', 'r', 'utf-8') as f:
        return f.read()


setup(
    name='flake8-string-format',
    version=get_version(),
    description='string format checker, plugin for flake8',
    long_description=get_long_description(),
    keywords='flake8 format',
    install_requires=['flake8'],
    maintainer='Fabian Neundorf',
    maintainer_email='CommodoreFabianus@gmx.de',
    url='https://github.com/xZise/flake8-string-format',
    license='MIT License',
    py_modules=['flake8_string_format'],
    zip_safe=False,
    entry_points={
        'flake8.extension': [
            'P = flake8_string_format:StringFormatChecker',
        ],
    },
    tests_require=['six'],
    test_suite='test_flake8_string_format',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Framework :: Flake8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ],
)
