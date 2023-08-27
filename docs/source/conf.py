# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'tumblr-dot-com'
copyright = '2023, James Ansley'
author = 'James Ansley'
release = '0.2.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx_rtd_theme',
]
autosummary_generate = True

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
add_module_names = False
autodoc_mock_imports = ['requests', "requests_oauthlib"]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": False,
    "imported-members": False,
    "python_use_unqualified_type_names": True,

}
autodoc_member_order = "bysource"
autodoc_typehints_format = "short"
python_use_unqualified_type_names = True

