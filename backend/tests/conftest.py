import os
import sys
import pytest

# Add the parent directory to sys.path to import the app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))