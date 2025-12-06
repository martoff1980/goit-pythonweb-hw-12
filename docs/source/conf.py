import os
import sys

conf_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(conf_dir, "..", ".."))
sys.path.insert(0, project_root)

# from routers.users import router as user_router 

language = "uk_UA"

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'API Contact Manager'
copyright = '2025, D. Breus'
author = 'D. Breus'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []

language = 'uk_UA'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_theme = 'alabaster'
html_static_path = ['_static']

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # подітримка Google/NumPy docstring
    "sphinx.ext.viewcode",  # ссилки на исходники
    "sphinx_autodoc_typehints",
]


templates_path = ["_templates"]
exclude_patterns = []

# Mock imports
autodoc_mock_imports = [
    "middleware",
    "config",
    "passlib", 
    "starlette",
    "database", 
    "sqlalchemy",
    "pydantic",
    "jose",
    "slowapi",
    "fastapi",
    "cloudinary",
    "redis",
    "fastapi_mail",
    ]

