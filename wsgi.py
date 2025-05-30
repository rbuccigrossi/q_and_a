import sys
import pathlib

# Make sure Python can find the module
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
if PROJECT_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, PROJECT_ROOT.as_posix())

# Import the Flask instance
from app import app as application
