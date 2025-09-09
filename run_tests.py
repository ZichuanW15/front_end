#!/usr/bin/env python3
"""
Simple Test Runner for Fractionalized Asset Ownership App

This is a convenience script that calls the comprehensive test runner.
For full testing options, use: python tests/run_all_tests.py

Usage:
    python run_tests.py [options]
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Main function - delegates to comprehensive test runner"""
    # Get the path to the comprehensive test runner
    tests_dir = Path(__file__).parent / 'tests'
    test_runner = tests_dir / 'run_all_tests.py'
    
    if not test_runner.exists():
        print("❌ Comprehensive test runner not found!")
        print(f"Expected location: {test_runner}")
        sys.exit(1)
    
    # Pass all arguments to the comprehensive test runner
    cmd = [sys.executable, str(test_runner)] + sys.argv[1:]
    
    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()