"""PEP-518 backwards compatibility."""
from setuptools import setup

setup(name="mk2", use_scm_version=True, setup_requires=["setuptools_scm"])
