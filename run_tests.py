"""Test runner script for pytest execution."""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import pytest

if __name__ == '__main__':
    """Execute pytest with predefined configuration.
    
    Runs all tests in the tests/ directory with:
    - Short traceback format for cleaner output
    - Disabled warning messages
    
    Returns:
        Exit code from pytest execution (0 for success, non-zero for failures)
        
    Example:
        >>> python run_tests.py
        ========== test session starts ==========
        ...
        ========== 25 passed in 2.34s ==========
    """
    sys.exit(pytest.main([
        'tests/',
        '-s',
        '--tb=short',
        '--disable-warnings'
    ]))
