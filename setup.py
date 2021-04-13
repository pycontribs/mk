"""PEP-518 backwards compatibility."""
import site
import sys

from setuptools import setup

# See https://github.com/pypa/pip/issues/7953
site.ENABLE_USER_SITE = "--user" in sys.argv[1:]

setup(
    name="mk",
    use_scm_version={"local_scheme": "no-local-version"},
    setup_requires=["setuptools_scm[toml]>=3.5.0"],
)
