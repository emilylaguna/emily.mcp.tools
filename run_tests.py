#!/usr/bin/env python3
"""
Test runner
"""

import sys
import pytest
from pathlib import Path

def main():
    """Run the tests."""
    # Add the project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Run all tests in the tests directory
    test_dir = project_root / "tests"
    
    if not test_dir.exists():
        print(f"Tests directory not found: {test_dir}")
        return 1
    
    print("Running all tests...")
    result = pytest.main([
        str(test_dir),
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
    ])
    
    return result

if __name__ == "__main__":
    sys.exit(main()) 