"""
FileReaderService — encapsulates all file I/O for the backend.

Reads binary content, validates size limits, and normalises errors
so the Electron IPC layer never touches bare ``fs`` calls.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Protocol, runtime_checkable


class FileReaderError(Exception):
    """Base exception for all file-reader failures."""

    code: str = "FILE_READER_ERROR"

    def __init__(
        self, message: str, code_attr: str | None = None
    ) -> None:  # noqa: N803
        super().__init__(message)
        self.message = message
        if code_attr:
            self.code = code_attr


class FileTooLargeError(FileReaderError):
    """Raised when a file exceeds the configured size limit."""

    code = "FILE_TOO_LARGE"


class FileReadError(FileReaderError):
    """Raised when the file cannot be read (permissions, missing, etc)."""

    code = "FILE_READ_ERROR"


@runtime_checkable
class IFileReader(Protocol):
    """Protocol for file-reader backends (sync or async)."""

    async def read(self, file_path: str, max_bytes: int | None = None) -> bytes:
        """Return the file content as bytes."""
        ...


class FileReaderService(IFileReader):
    """
    Production file reader.

    * Checks file size before reading
    * Normalises OS-level IO errors into domain exceptions
    * Pure async via asyncio.to_thread (never blocks the event loop)
    """

    def __init__(self, default_max_bytes: int = 20 * 1024 * 1024) -> None:
        """
        :param default_max_bytes: Maximum allowed file size in bytes (default 20 MB).
        """
        self._default_max_bytes = default_max_bytes

    async def read(self, file_path: str, max_bytes: int | None = None) -> bytes:
        limit = max_bytes if max_bytes is not None else self._default_max_bytes
        path = Path(file_path)

        # —— Size guard ——
        try:
            stat = await asyncio.to_thread(path.stat)
        except FileNotFoundError as exc:
            raise FileReadError(
                f"File not found: {file_path}", "FILE_NOT_FOUND"
            ) from exc
        except OSError as exc:
            raise FileReadError(f"Cannot stat file: {exc}", "FILE_STAT_ERROR") from exc

        if stat.st_size > limit:
            raise FileTooLargeError(
                f"File {path.name} ({stat.st_size} bytes) exceeds limit {limit} bytes",
            )

        # —— Read guard ——
        try:
            return await asyncio.to_thread(path.read_bytes)
        except OSError as exc:
            raise FileReadError(
                f"Failed to read file: {exc}", "FILE_READ_ERROR"
            ) from exc

    async def read_chunks(
        self,
        file_path: str,
        chunk_size: int = 64 * 1024,
        max_bytes: int | None = None,
    ) -> bytes:
        """
        Memory-efficient streaming read.

        Returns full content as bytes (caller can wrap in a generator if needed).
        """
        limit = max_bytes if max_bytes is not None else self._default_max_bytes
        path = Path(file_path)
        total = 0
        chunks: list[bytes] = []

        def _read() -> list[bytes]:
            with path.open("rb") as fh:
                local_chunks: list[bytes] = []
                while True:
                    data = fh.read(chunk_size)
                    if not data:
                        break
                    local_chunks.append(data)
                return local_chunks

        try:
            chunks = await asyncio.to_thread(_read)
        except FileNotFoundError as exc:
            raise FileReadError(
                f"File not found: {file_path}", "FILE_NOT_FOUND"
            ) from exc
        except OSError as exc:
            raise FileReadError(
                f"Failed to read file: {exc}", "FILE_READ_ERROR"
            ) from exc

        total = sum(len(c) for c in chunks)
        if total > limit:
            raise FileTooLargeError(
                f"File {path.name} ({total} bytes) exceeds limit {limit} bytes",
            )

        return b"".join(chunks)
