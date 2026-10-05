1.7.0 / 2024-10-11
===================
  * Allow raw numeric values to be used as keys
  * Add `wherenot`
  * Added EZRegex pattern for the split extension regex
  * Added negative and * indices and quotes to `Split` parameters
  * Typo: duplicate line removed.
  * Added `path` extension that exposes datum's path from the jsonpath expression itself.
  * Remove Python 3.7 support
  *  Only construct the parse table once
  * updated test for `jsonpath.py` changes
  * fix for Updating a json object fails if the value of a key is boolean #73
  * Add Codespaces configuration
  * Add `.editorconfig`
  * Fix a GitHub workflow schema issue

1.6.1 / 2024-01-11
===================
  * Bump actions/setup-python from 4 to 5
  * Bump github/codeql-action from 2 to 3
  * Use tox to run the test suite against all supported Pythons
  * Fix a typo in the README
  * Add a test case
  * Fix issue with lambda based updates
  * Remove unused code from the test suite
  * Refactor `tests/test_parser.py`
  * Refactor `tests/test_lexer.py`
  * Refactor `tests/test_jsonpath_rw_ext.py`
  * De-duplicate the parser test cases
  * Refactor `tests/test_jsonpath.py`
  * Refactor `tests/test_jsonpath.py`
  * Refactor `tests/test_exceptions.py`
  * Remove a test that merely checks exception inheritance
  * Refactor `tests/test_examples.py`
  * Add pytest-randomly to shake out auto_id side effects
  * Bump actions/checkout from 3 to 4
  * Include the test suite in coverage reports
  * Remove tests that don't affect coverage and contribute nothing
  * Reformat `tests/test_create.py`
  * Remove `test_doctests`, which is a no-op
  * Demonstrate that there are no doctests
  * Remove the `coveralls` dependency
  * Migrate `tests/bin/test_jsonpath.py` to use pytest
  * remove Python2 crumbs
  * Add CodeQL analysis
  * Remove the `oslotest` dependency
  * Fix running CI against incoming PRs
  * Support, and test against, Python 3.12
  * Update the currently-tested CPython versions in the README
  * Remove an unused Travis CI config file
  * Add a Dependabot config to keep GitHub action versions updated
  * add a test for the case when root element is a list
  * Fix issue with assignment in case root element is a list.
  * Fix typo in README
  * Fix test commands in Makefile
  * Fix .coveragerc path
  * Simplify clean in Makefile
  * Refactor unit tests for better errors
  * test case for existing auto id
  * Add more examples to README (thanks @baynes)
  * fixed typo
  * Don't fail when regex match is attempted on non-strings
  * added step in slice
  * Add additional tests
  * Add `keys` keyword

1.6.0 / 2023-09-13
===================
  *  Enclose field names containing literals in quotes
  *  Add note about extensions
  *  Remove documentation status link
  *  Update supported versions in setup.py
  *  Add LICENSE file
  *  Code cleanup
  *  Remove dependency on six
  *  Update build status badge
  *  (origin/github-actions, github-actions) Remove testscenarios dependency
  *  Remove pytest version constraints
  *  Add testing with GitHub actions
  *  Escape back slashes in tests to avoid DeprecationWarning.
  *  Use raw strings for regular expressions to avoid DeprecationWarning.
  *  refactor(package): remove dependency for decorator
  *  Merge pull request #128 from michaelmior/hashable
  *  Make path instances hashable
  *  Merge pull request #122 from snopoke/snopoke-patch-1
  *  Add more detail to filter docs.
  *  remove incorrect parenthesis in filter examples
  *  Merge pull request #119 from snopoke/patch-1
  *  add 'sub' line with function param names
  *  readme formatting fixes
  *  chore(history): update
  *  Update __init__.py

1.5.3 / 2021-07-05
==================

  * Update __init__.py
  * Update setup.py
  * Merge pull request #72 from kaapstorm/find_or_create
  * Tests
  * Add `update_or_create()` method
  * Merge pull request #68 from kaapstorm/example_tests
  * Merge pull request #70 from kaapstorm/exceptions
  * Add/fix `__eq__()`
  * Add tests based on Stefan Goessner's examples
  * Tests
  * Allow callers to catch JSONPathErrors

v1.5.2 / 2020-09-07
===================

  * Merge pull request #41 from josephwhite13/allow-dictionary-filtering
  * Merge pull request #48 from back2root/master
  * Check for null value.
  * Merge pull request #40 from memborsky/add-regular-expression-contains-support
  * feat: support regular expression for performing contains (=~) filtering
  * if datum.value is a dictionary, filter on the list of values

1.5.1 / 2020-03-09
==================

  * feat(version): bump
  * fix(setup): strip extension

v1.5.0 / 2020-03-06
===================

  * feat(version): bump to 1,5.0
  * Merge pull request #13 from dcreemer/master
  * fix(travis): remove python 3.4 (deprecated)
  * refactor(docs): delete coverage badge
  * Merge pull request #25 from rahendatri/patch-1
  * Merge pull request #26 from guandalf/contains_operator
  * Merge pull request #31 from borysvorona/master
  * refactor(travis): update python versions
  * Merge pull request #34 from dchourasia/patch-1
  * Updated Filter.py to implement update function
  * added hook for catching null value instead of empty list in path
  * Ignore vscode folder
  * Contains operator implementation
  * Update requirements-dev.txt
  * setuptools>=18.5
  * update setuptools
  * update cryptography
  * new version of cryptography requires it
  * entry point conflict with https://pypi.org/project/jsonpath/
  * add str() method
  * clean up
  * remove extra print()
  * refactor(docs): remove codesponsor
  * feat(docs): add sponsor banner
  * Update .travis.yml
  * feat(History): add History file
  * fix(travis-ci): ignore versions
  * feat(requirements): add missing pytest-cov dependency
  * refactor(requirements): use version constraint
  * fix: remove .cache files
  * feat: add required files
  * fix(travis-ci): install proper packages
  * refactor(setup.py): update description
  * refactor(docs): remove downloads badge
  * fix(tests): pass unit tests
  * feat(docs): add TravisCI and PyPI badges
  * Merge pull request #2 from tomas-fp/master
  * feat(docs): update readme notes
  * feat(setup): increase version
  * Merge pull request #1 from kmmbvnr/patch-1
  * Fix github url on pypi

v1.4.3 / 2017-08-24
===================

  * fix(travis-ci): ignore versions
  * feat(requirements): add missing pytest-cov dependency
  * refactor(requirements): use version constraint
  * fix: remove .cache files
  * feat: add required files
  * fix(travis-ci): install proper packages
  * refactor(setup.py): update description
  * refactor(docs): remove downloads badge
  * fix(tests): pass unit tests
  * feat(docs): add TravisCI and PyPI badges
  * Merge pull request #2 from tomas-fp/master
  * feat(docs): update readme notes
  * feat(setup): increase version
  * Merge pull request #1 from kmmbvnr/patch-1
  * Fix github url on pypi
