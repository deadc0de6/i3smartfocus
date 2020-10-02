from setuptools import setup, find_packages
from i3smartfocus.i3smartfocus import VERSION
from codecs import open
from os import path

readme = 'README.md'
here = path.abspath(path.dirname(__file__))

try:
    from pypandoc import convert_file
    read_readme = lambda f: convert_file(f, 'rst')
except ImportError:
    print('\n[WARNING] pypandoc not found, could not convert \"{}\"\n'.format(readme))
    read_readme = lambda f: open(f, 'r').read()

VERSION = VERSION
REQUIRES_PYTHON = '>=3.4'

setup(
    name='i3smartfocus',
    version=VERSION,

    description='i3wm smart focus',
    long_description=read_readme(readme),
    url='https://github.com/deadc0de6/i3smartfocus',
    download_url = 'https://github.com/deadc0de6/i3smartfocus/archive/v'+VERSION+'.tar.gz',

    author='deadc0de6',
    author_email='deadc0de6@foo.bar',

    license='GPLv3',
    python_requires=REQUIRES_PYTHON,
    classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          ],

    keywords='i3wm tiling focus',
    packages=find_packages(exclude=['tests*']),
    install_requires=['i3ipc'],

    extras_require={
        'dev': ['check-manifest'],
        'test': ['pycodestyle', 'pyflakes'],
    },

    entry_points={
          'console_scripts': [
                'i3smartfocus=i3smartfocus.i3smartfocus:main',
                ],
          },
)
