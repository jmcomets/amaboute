#!/usr/bin/env python

import os
from setuptools import setup, find_packages

def read_lines_if_exists(filename, relative_from_here=False):
    if relative_from_here:
        this_dir = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(this_dir, filename)
    try:
        with open(filename) as fp:
            return [line.rstrip("\n") for line in fp if line]
    except IOError:
        return []

setup(name="amaboute",
      version="0.0.1",
      description="Impersonator bot",
      long_description="Amaboute imitates other people in a Telegram chat and can generate conversations between people in the chat",
      author="Jean-Marie Comets",
      author_email="jean.marie.comets@gmail.com",
      python_requires=">=3.5.0",
      url="https://github.com/jmcomets/amaboute",
      packages=find_packages("src"),
      package_dir={"": "src"},
      entry_points={ "console_scripts": ["amaboute=amaboute.app:main"] },
      install_requires=read_lines_if_exists("requirements.txt", relative_from_here=True),
      tests_requires=read_lines_if_exists("test-requirements.txt", relative_from_here=True),
      setup_requires=["pytest-runner"],
      include_package_data=True,
      license="MIT",
      )
