import pathlib
import tomllib

# General configuration
# ---------------------

# The suffix of source filenames.
source_suffix = {".rst": "restructuredtext"}

# The main toctree document.
master_doc = "index"

# General information about the project.
project = "jsonpath-ng"

# Extract the project version.
pyproject_ = pathlib.Path(__file__).parent.parent / "pyproject.toml"
info_ = tomllib.loads(pyproject_.read_text())
version = release = info_["project"]["version"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# Don't show "Powered by" text.
html_show_sphinx = False

nitpicky = True

extensions = [
    "sphinx_issues",
]

# `sphinx_issues` configuration
# -----------------------------

issues_github_path = "jsonpath-ng/jsonpath-ng"


# HTML theme configuration
# ------------------------

html_theme = "alabaster"
html_theme_options = {
    # Link to GitHub
    "github_user": "jsonpath-ng",
    "github_repo": "jsonpath-ng",
    "github_button": True,
    "github_type": "star",
    "github_count": False,
}

# Don't copy source .rst files into the built documentation.
html_copy_source = False
