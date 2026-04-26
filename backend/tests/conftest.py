"""Test conftest: sets up PYTHONPATH and imports all fixtures."""
import sys
from pathlib import Path

# Add project root to PYTHONPATH so `backend.app.*` imports resolve
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

pytest_plugins = [
    "backend.tests.fixtures.db",
    "backend.tests.fixtures.ollama",
]
