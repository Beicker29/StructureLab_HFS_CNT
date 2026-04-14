"""Public package interface for the steel connections engine."""

from .models.errors import StructuredError
from .models.input import InputCase, parse_input_case, parse_input_case_file
from .models.output import CheckResult, DetailedRunResult

__all__ = [
    "InputCase",
    "CheckResult",
    "DetailedRunResult",
    "StructuredError",
    "parse_input_case",
    "parse_input_case_file",
]
