Contributing
############

Reporting an issue
==================

Before reporting an issue, please check to see if it has already been reported.

Then, before opening a new issue, please collect this information:

*   The operating system
*   The Python version (run ``python -VV`` and paste the output)
*   The jsonpath-ng version (run ``python -m pip list`` and paste the output)
*   A minimal code example that reproduces the issue you're reporting
*   If you're seeing a Python exception, include the full traceback

Include all of that information when opening an issue.


Opening a PR
============

Before opening a PR, please follow these guidelines when creating commits:

*   Only make minimal changes.

    Small PRs are easier to review.

*   Where appropriate, add tests to demonstrate your code changes work.

    Bug fixes and features generally require tests.

*   Describe your changes in a changelog fragment.

    Run ``scriv create`` to generate the changelog fragment in ``changelog.d/``
    and edit the fragment to document what your PR is changing.

*   If your change fixes an open issue, reference the issue in your commit body.

    For example, write "Closes #123" or "Fixes #123".


AI policy
=========

You are responsible for the issues and PRs that you open, and for code that you submit.
This was true before AI became widely available, and it remains true.

The time that maintainers spend on the project is uncompensated and limited.
Please be respectful of others by reviewing and testing your changes
before opening a PR.

Issues and PRs that appear to lack human oversight will be closed.


Setting up a development environment
====================================

Clone the git repository.

Install the project in editable mode with development tools:

..  code-block::

    python -m pip install -e. --group=dev

Before making changes, confirm that the test suite passes in your environment:

..  code-block::

    tox

After making changes, run the test suite locally again.
