#!/usr/bin/env python3
"""
Test runner script for the Mergington High School Activities API
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests with coverage"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    python_path = os.path.join(project_root, ".venv", "bin", "python")
    
    if not os.path.exists(python_path):
        python_path = "python"  # Fallback to system python
    
    try:
        # Run tests with coverage
        result = subprocess.run([
            python_path, "-m", "pytest", 
            "tests/", 
            "--cov=src", 
            "--cov-report=term-missing",
            "--cov-report=html",
            "-v"
        ], cwd=project_root)
        
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

def run_tests_only():
    """Run tests without coverage"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    python_path = os.path.join(project_root, ".venv", "bin", "python")
    
    if not os.path.exists(python_path):
        python_path = "python"
    
    try:
        result = subprocess.run([
            python_path, "-m", "pytest", 
            "tests/", 
            "-v"
        ], cwd=project_root)
        
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--no-coverage":
        exit_code = run_tests_only()
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)