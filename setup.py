#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup script for RedBench"""

import os
from setuptools import setup, find_packages

# Get the long description from the README file
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Define package metadata
NAME = "redeval"
VERSION = "0.1.0"
DESCRIPTION = "Redbench: A Universal Dataset for Comprehensive Red Teaming of Large Language Models"
AUTHOR = "Knovel Engineering Lab"
AUTHOR_EMAIL = "andrew.dang@knoveleng.com"
URL = "https://github.com/knoveleng/redbench"
LICENSE = "MIT" 

# Define package dependencies
REQUIRED_PACKAGES = [
    "vllm",
    "openai",
    "pydantic",
    "PyYAML",
    "datasets",
]

# Define development dependencies
DEV_PACKAGES = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    include_package_data=True,
    install_requires=REQUIRED_PACKAGES,
    extras_require={
        "dev": DEV_PACKAGES,
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="llm, language-model, evaluation, robustness, ai-safety",
    project_urls={
        "Bug Reports": f"{URL}/issues",
        "Source": URL,
    },
)