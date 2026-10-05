import io
import setuptools


setuptools.setup(
    name='jsonpath-ng',
    version='1.8.0',
    description=(
        'A final implementation of JSONPath for Python that aims to be '
        'standard compliant, including arithmetic and binary comparison '
        'operators and providing clear AST for metaprogramming.'
    ),
    author='Tomas Aparicio',
    author_email='tomas@aparicio.me',
    url='https://github.com/jsonpath-ng/jsonpath-ng',
    license='Apache 2.0',
    long_description=io.open('README.rst', encoding='utf-8').read(),
    packages=['jsonpath_ng', 'jsonpath_ng.bin', 'jsonpath_ng.ext','jsonpath_ng._ply'],
    entry_points={
        'console_scripts': [
            'jsonpath_ng=jsonpath_ng.bin.jsonpath:entry_point'
        ],
    },
    test_suite='tests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Programming Language :: Python :: 3.15',
    ],
)
