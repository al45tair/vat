# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

with open('README.rst', 'rb') as f:
    long_desc = f.read().decode('utf-8')
        
setup(
    name='vat',
    version='0.2.0',
    description='A python package for dealing with VAT',
    long_description=long_desc,
    author='Alastair Houghton',
    author_email='alastair@alastairs-place.net',
    url='http://bitbucket.org/al45tair/vat',
    license='MIT License',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Topic :: Office/Business :: Financial',
        ],
    package_data = {
        'vat': ['gb/moss/resources/*']
        },
    tests_require=['pytest'],
    cmdclass={
        'test': PyTest
        },
    install_requires=[
        'six',
        'lxml >= 3.4.0',
        'python-dateutil >= 1.5',
        'python-Levenshtein >= 0.11.2',
        ],
    provides=['vat']
    )
