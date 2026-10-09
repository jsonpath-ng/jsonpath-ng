..
    THIS FILE IS MANAGED BY SCRIV.
    DO NOT MANUALLY ADD CONTENT TO THIS FILE.

CHANGELOG
#########

    Unreleased changes can be found in
    `the changelog.d/ directory <https://github.com/jsonpath-ng/jsonpath-ng/tree/HEAD/changelog.d>`_.

..  scriv-insert-here

.. _changelog-1.10.0:

1.10.0 - 2026-10-09
===================

Changed
-------

*   Use pre-generated PLY lex/parse tables. (#121)

    Base parser instantiation is now over 20 times faster,
    and extended parser instantiation is over 50 times faster.
    In addition, actual parsing is over 50% faster.

    This change also allows downstream projects
    to run with Python optimizations enabled.

Deprecated
----------

*   The ``debug`` parameter, given when instantiating lexers and parsers,
    is now deprecated and has no effect.

    The ``debug`` parameter will be removed in version 2.0.0.

    To prepare for the change, remove the parameter from instantiation sites.

*   The ``ExtentedJsonPathParser``, which was renamed in v1.8.0,
    is now deprecated.

    The ``ExtentedJsonPathParser`` name will be removed in version 2.0.0.

    To prepare for the change, use the name ``ExtendedJsonPathParser``.

*   The ``jsonpath_ng.__version__`` attribute is now deprecated.

    The ``__version__`` attribute will be removed in version 2.0.0.

    To prepare for the change, import ``importlib.metadata``
    and use ``importlib.metadata.version("jsonpath-ng")``
    to get the package version.

Project administration
----------------------

*   Use Trusted Publishing in CI to publish to PyPI.
*   Use CodSpeed to track runtime performance.
*   Add a suite of pre-commit linters and fixers to enforce code standards.
*   Use scriv to manage the changelog.

    This eliminates trivial merge conflicts in PRs
    caused by overlapping CHANGELOG updates.

.. _changelog-1.9.1:

1.9.1 - 2026-10-06
==================

Fixed
-----

- Add ``requires-python`` to the project metadata in ``pyproject.toml``. (#266)

  This ensures the package can only be installed on supported Python versions.

.. _changelog-1.9.0:

1.9.0 - 2026-10-05 [YANKED]
===========================

   NOTE: This version was yanked from PyPI.

   It could be installed on unsupported Python versions
   due to a missing ``requires-python`` in the project metadata.

   This was fixed in v1.9.1.

Added
-----

- Support Python 3.15.
- Add a ``py.typed`` marker.
- Support negation of relative existence queries in extended filter expressions (e.g. ``$[?(!@.field)]``).

Fixed
-----

- Ignore non-mapping values when updating named fields instead of raising ``TypeError`` (#104).

- Return no matches for negative array indices beyond the start of an array,
  matching the behavior of out-of-range positive indices (#203).

- Fix extended filter equality against an integer literal truncating float values,
  so ``[?(@.v = 0)]`` no longer matches an element with ``v = 0.6`` (#227).

- ``update()`` with an in-place callback returning ``None`` no longer overwrites the field with ``None`` (#163)

- Fix an ``AttributeError`` that occurs when an ``Index`` instance is hashed. (#224)

- ``Index.find`` no longer raises ``KeyError`` when applied to a dict
  (e.g. ``$.*[0]``, where ``*`` matched a dict value).
  It now matches nothing, as the docstring promises. (#93)

- Fix extended parser handling of field names that start with ``true`` or ``false``.

- Stop serializing ``Child`` paths with surrounding parentheses. (#215)

- Avoid mutating dictionaries while evaluating extended filter expressions.

- ``str()`` of an ``Index`` with comma-separated indices (e.g. ``[0,1]``) no longer raises ``TypeError``.

- Fix broken ``Slice`` serialization behavior.

  Previously, a slice like ``[0:]`` would serialize to ``[]``,
  and a slice like ``[::2]`` would serialize to ``[:2]``.

Removed
-------

- Drop support for Python 3.10.

.. _changelog-1.8.0:

1.8.0 - 2026-02-24
==================

Added
-----

- Support Python 3.13 and 3.14
- Typing for IDE autocomplete
- Support for EMOJI and CJK Unicode
- Support for ``DatumInContext`` in-place updating
- Support equality checking of ``Operation`` instances
- Support string serialization of ``Union`` and ``Intersect`` instances
- Support comma-separated indices
- Add some type annotations

Changed
-------

- Rename ``ExtentedJsonPathParser``
- Remove ply dependency

Fixed
-----

- ``[*]`` now correctly returns results when applied to a ``False`` or other falsy non-``None`` value;
  previously it returned an empty list (#198).
- ``update()`` no longer raises ``TypeError`` when a value in the data structure is a boolean (#73).
- ``update_or_create()`` now works correctly when the root data structure is a list (#108).
- Fix single constant case
- Update field filter to resolve wildcard path issue
- Vendor copy of ply and remove pickle support from the vendored copy to resolve `CVE-2025-56005 <https://nvd.nist.gov/vuln/detail/CVE-2025-56005>`__
- Fix string serialization throughout the library to enforce roundtrip parsing consistency.

  - Fields are more conservatively enclosed in quotion marks
    This fixes serialization and re-parsing of ``"00"``, ``'%'``, ``'0@'`` and ``"&'"``.
  - ``Operation`` instances can now be serialized.
    This fixes serialization of ``0-@`` and ``A -A``.
  - ``SortedThis`` instances can now be serialized and re-parsed.
    This fixes serialization of ``0[/0]``.
  - ``Child`` precedence is now preserved using parentheses during serialization.
    This ensures that serialized strings like ``a..b[c]`` serialize and re-parse identically.

- Fix parsing and string serialization of numeric-only identifiers.
  This fixes parsing of ``10``, which was parsed as two separate fields.
- Fix equality checks for ``SortedThis`` instances.
- Fix bool filter type to handle None values

Removed
-------

- Python 3.8 and 3.9 no longer supported

.. _changelog-1.7.0:

1.7.0 - 2024-10-11
==================

- Allow raw numeric values to be used as keys
- Add ``wherenot``
- Added EZRegex pattern for the split extension regex
- Added negative and \* indices and quotes to ``Split`` parameters
- Typo: duplicate line removed.
- Added ``path`` extension that exposes datum's path from the jsonpath expression itself.
- Remove Python 3.7 support
- Only construct the parse table once
- updated test for ``jsonpath.py`` changes
- fix for Updating a json object fails if the value of a key is boolean #73
- Add Codespaces configuration
- Add ``.editorconfig``
- Fix a GitHub workflow schema issue

.. _changelog-1.6.1:

1.6.1 - 2024-01-11
==================

- Bump actions/setup-python from 4 to 5
- Bump github/codeql-action from 2 to 3
- Use tox to run the test suite against all supported Pythons
- Fix a typo in the README
- Add a test case
- Fix issue with lambda based updates
- Remove unused code from the test suite
- Refactor ``tests/test_parser.py``
- Refactor ``tests/test_lexer.py``
- Refactor ``tests/test_jsonpath_rw_ext.py``
- De-duplicate the parser test cases
- Refactor ``tests/test_jsonpath.py``
- Refactor ``tests/test_jsonpath.py``
- Refactor ``tests/test_exceptions.py``
- Remove a test that merely checks exception inheritance
- Refactor ``tests/test_examples.py``
- Add pytest-randomly to shake out auto_id side effects
- Bump actions/checkout from 3 to 4
- Include the test suite in coverage reports
- Remove tests that don't affect coverage and contribute nothing
- Reformat ``tests/test_create.py``
- Remove ``test_doctests``, which is a no-op
- Demonstrate that there are no doctests
- Remove the ``coveralls`` dependency
- Migrate ``tests/bin/test_jsonpath.py`` to use pytest
- remove Python2 crumbs
- Add CodeQL analysis
- Remove the ``oslotest`` dependency
- Fix running CI against incoming PRs
- Support, and test against, Python 3.12
- Update the currently-tested CPython versions in the README
- Remove an unused Travis CI config file
- Add a Dependabot config to keep GitHub action versions updated
- add a test for the case when root element is a list
- Fix issue with assignment in case root element is a list.
- Fix typo in README
- Fix test commands in Makefile
- Fix .coveragerc path
- Simplify clean in Makefile
- Refactor unit tests for better errors
- test case for existing auto id
- Add more examples to README (thanks @baynes)
- fixed typo
- Don't fail when regex match is attempted on non-strings
- added step in slice
- Add additional tests
- Add ``keys`` keyword

.. _changelog-1.6.0:

1.6.0 - 2023-09-13
==================

- Enclose field names containing literals in quotes
- Add note about extensions
- Remove documentation status link
- Update supported versions in setup.py
- Add LICENSE file
- Code cleanup
- Remove dependency on six
- Update build status badge
- (origin/github-actions, github-actions) Remove testscenarios dependency
- Remove pytest version constraints
- Add testing with GitHub actions
- Escape back slashes in tests to avoid DeprecationWarning.
- Use raw strings for regular expressions to avoid DeprecationWarning.
- refactor(package): remove dependency for decorator
- Merge pull request #128 from michaelmior/hashable
- Make path instances hashable
- Merge pull request #122 from snopoke/snopoke-patch-1
- Add more detail to filter docs.
- remove incorrect parenthesis in filter examples
- Merge pull request #119 from snopoke/patch-1
- add 'sub' line with function param names
- readme formatting fixes
- chore(history): update
- Update **init**.py

.. _changelog-1.5.3:

1.5.3 - 2021-07-05
==================

- Update **init**.py
- Update setup.py
- Merge pull request #72 from kaapstorm/find_or_create
- Tests
- Add ``update_or_create()`` method
- Merge pull request #68 from kaapstorm/example_tests
- Merge pull request #70 from kaapstorm/exceptions
- Add/fix ``__eq__()``
- Add tests based on Stefan Goessner's examples
- Tests
- Allow callers to catch JSONPathErrors

.. _changelog-1.5.2:

1.5.2 - 2020-09-07
==================

- Merge pull request #41 from josephwhite13/allow-dictionary-filtering
- Merge pull request #48 from back2root/master
- Check for null value.
- Merge pull request #40 from memborsky/add-regular-expression-contains-support
- feat: support regular expression for performing contains (=~) filtering
- if datum.value is a dictionary, filter on the list of values

.. _changelog-1.5.1:

1.5.1 - 2020-03-09
==================

- feat(version): bump
- fix(setup): strip extension

.. _changelog-1.5.0:

1.5.0 - 2020-03-06
==================

- feat(version): bump to 1,5.0
- Merge pull request #13 from dcreemer/master
- fix(travis): remove python 3.4 (deprecated)
- refactor(docs): delete coverage badge
- Merge pull request #25 from rahendatri/patch-1
- Merge pull request #26 from guandalf/contains_operator
- Merge pull request #31 from borysvorona/master
- refactor(travis): update python versions
- Merge pull request #34 from dchourasia/patch-1
- Updated Filter.py to implement update function
- added hook for catching null value instead of empty list in path
- Ignore vscode folder
- Contains operator implementation
- Update requirements-dev.txt
- setuptools>=18.5
- update setuptools
- update cryptography
- new version of cryptography requires it
- entry point conflict with https://pypi.org/project/jsonpath/
- add str() method
- clean up
- remove extra print()
- refactor(docs): remove codesponsor
- feat(docs): add sponsor banner
- Update .travis.yml
- feat(History): add History file
- fix(travis-ci): ignore versions
- feat(requirements): add missing pytest-cov dependency
- refactor(requirements): use version constraint
- fix: remove .cache files
- feat: add required files
- fix(travis-ci): install proper packages
- refactor(setup.py): update description
- refactor(docs): remove downloads badge
- fix(tests): pass unit tests
- feat(docs): add TravisCI and PyPI badges
- Merge pull request #2 from tomas-fp/master
- feat(docs): update readme notes
- feat(setup): increase version
- Merge pull request #1 from kmmbvnr/patch-1
- Fix github url on pypi

.. _changelog-1.4.3:

1.4.3 - 2017-08-24
==================

- fix(travis-ci): ignore versions
- feat(requirements): add missing pytest-cov dependency
- refactor(requirements): use version constraint
- fix: remove .cache files
- feat: add required files
- fix(travis-ci): install proper packages
- refactor(setup.py): update description
- refactor(docs): remove downloads badge
- fix(tests): pass unit tests
- feat(docs): add TravisCI and PyPI badges
- Merge pull request #2 from tomas-fp/master
- feat(docs): update readme notes
- feat(setup): increase version
- Merge pull request #1 from kmmbvnr/patch-1
- Fix github url on pypi
