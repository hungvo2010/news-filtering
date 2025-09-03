"""
Unit tests for basic project setup verification.
"""

import sys
import os
import pytest

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_dependencies_import():
    """Test that all required dependencies can be imported."""
    try:
        import requests
        import bs4
        from dotenv import load_dotenv
        from apscheduler.schedulers.blocking import BlockingScheduler
        import responses
    except ImportError as e:
        pytest.fail(f"Failed to import required dependency: {e}")


def test_project_structure():
    """Test that project directory structure exists."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    required_dirs = ['src', 'tests', 'config']
    for dir_name in required_dirs:
        dir_path = os.path.join(base_dir, dir_name)
        assert os.path.exists(dir_path), f"Directory {dir_name} does not exist"
        assert os.path.isdir(dir_path), f"{dir_name} is not a directory"


def test_requirements_file():
    """Test that requirements.txt exists and contains expected packages."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    requirements_file = os.path.join(base_dir, 'requirements.txt')
    
    assert os.path.exists(requirements_file), "requirements.txt does not exist"
    
    with open(requirements_file, 'r') as f:
        content = f.read()
    
    expected_packages = ['requests', 'beautifulsoup4', 'python-dotenv', 'APScheduler', 'pytest']
    for package in expected_packages:
        assert package in content, f"Package {package} not found in requirements.txt"