"""PEP-518 backwards compatibility."""
from setuptools import setup

setup(
    name="mk",
    use_scm_version={"local_scheme": "no-local-version"},
    setup_requires=["setuptools_scm[toml]>=3.5.0"],
)
