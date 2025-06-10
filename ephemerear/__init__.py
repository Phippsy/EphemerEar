"""Convenience imports for the :mod:`ephemerear` package."""

from .EphemerEar import *
from .transcribe import *

# Provide access to the function helpers under a capitalised module name
# for compatibility with existing code and tests.
from . import functions as Functions
