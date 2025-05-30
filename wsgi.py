"""WSGI entry point for running the Audience Q&A app."""

import os
import sys
import pathlib

# Make sure Python can find the module
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
if PROJECT_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, PROJECT_ROOT.as_posix())

# Ensure working directory matches project root
os.chdir(PROJECT_ROOT)

# Import the Flask instance
from app import app as application
