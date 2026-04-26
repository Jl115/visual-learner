"""Test conftest: sets up PYTHONPATH and imports all fixtures."""
import sys
from pathlib import Path

# Add project root to PYTHONPATH
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

pytest_plugins = [
    "tests.fixtures.db",
    "tests.fixtures.ollama",
]
