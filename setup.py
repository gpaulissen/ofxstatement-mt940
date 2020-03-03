#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Setup
"""

import sys
from setuptools import find_packages
from setuptools.command.test import test as TestCommand
from distutils.core import setup

# To prevent importing about and thereby breaking the coverage info we use this
# exec hack
about = {}
with open('__about__.py') as fp:
    exec(fp.read(), about)


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', 'Arguments to pass to pytest')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import shlex
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


tests_require = [
    'pyyaml',
    'pytest',
    'pytest-cache',
    'pytest-cover',
    'pytest-flakes',
    'pytest-pep8',
    'flake8',
]


if sys.argv[-1] == 'info':
    for k, v in about.items():
        print('%s: %s' % (k, v))
    sys.exit()


if __name__ == '__main__':
    with open('README.md') as f:
        readme = f.read()

    try:
        import git
        try:
            repo = git.Repo('.')
        except git.exc.InvalidGitRepositoryError:
            raise ImportError()

        if repo.bare:
            raise ImportError()

        tags = [tag.tag for tag in repo.tags if tag.tag]
        tags = sorted(tags, key=lambda tag: tag.tagged_date, reverse=True)
        changes = [
            '',
            '',
            'Changelog',
            '---------',
        ]

        for tag in tags:
            version = tag.tag
            if version[0] != 'v':
                version = 'v' + version

            message = tag.message.split('\n')[0]
            changes.append(' * **%s** %s' % (version, message))

        changes = '\n'.join(changes)
    except ImportError:
        changes = ''

    setup(
        name=about['__package_name__'],
        version=about['__version__'],
        author=about['__author__'],
        author_email=about['__email__'],
        description=about['__description__'],
        url=about['__url__'],
        license=about['__license__'],
        keywords=["ofx", "banking", "statement", "ing"],
        packages=find_packages('src'),
        package_dir={'': 'src'},
#        namespace_packages=["ofxstatement", "ofxstatement.plugins"],
        long_description=readme + changes,
        long_description_content_type='text/markdown',
        include_package_data=True,
        install_requires=['ofxstatement'],
        tests_require=["pytest"],
        setup_requires=[
            'setuptools>=39.1.0',
        ],
        zip_safe=True,
        cmdclass={'test': PyTest},
        extras_require={'test': ["pytest"]},
        classifiers=[
            'Development Status :: 6 - Mature',
            'Programming Language :: Python :: 3',
            'Natural Language :: English',
            'Topic :: Office/Business :: Financial :: Accounting',
            'Topic :: Utilities',
            'Environment :: Console',
            'Operating System :: OS Independent',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
        ],
        entry_points={
            'ofxstatement':
            ['ingnl = ofxstatement.plugins.ingnl:IngNlPlugin']
        },
    )
