import hashlib
from typing import Any


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def truncate(text: str, max_len: int = 200) -> str:
    return text if len(text) <= max_len else text[:max_len] + "..."
