#!/usr/bin/env python3
from distutils.core import setup
setup(name="pass-rotate",
        author="Drew DeVault",
        author_email="sir@cmpwn.com",
        url="https://github.com/SirCmpwn/pass-rotate",
        description="Automatically rotates passwords on various web services",
        license="MIT",
        version="1.0",
        scripts=["pass-rotate"],
        packages=["passrotate"],
        install_requires=["beautifulsoup4", "requests"])
