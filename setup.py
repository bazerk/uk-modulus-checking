# override for holvi pypi
from distutils.core import setup

setup(
    name='ukmodulus',
    packages=['ukmodulus'],
    version='0.1.3',
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
    },
    description='Implementation of VocaLinks UK Modulus checking for UK account numbers and sort codes',
    author='Andrew Barrett',
    author_email='bazerk+pypy@gmail.com',
    url='https://github.com/holvi/uk-modulus-checking',
    download_url='https://github.com/holvi/uk-modulus-checking/tarball/0.1.3',
    keywords=['uk', 'banking', 'validation'],
    classifiers=[],
    licence='MIT',
)
