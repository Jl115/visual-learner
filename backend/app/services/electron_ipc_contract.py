"""
ElectronIpcContract — type-safe interface definitions for Electron ↔ backend IPC.

This module is the *single source of truth* for every channel name,
payload shape, and return type shared between:

  • electron/main.ts       (ipcMain.handle)
  • electron/preload.ts    (ipcRenderer.invoke)
  • renderer (Vue)         (window.api)
  • backend (FastAPI)      (upload router)

The classes below are pure data-contracts; they carry no Electron runtime
imports so they can be imported by backend unit tests and type-checked safely.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar, runtime_checkable


# ---------------------------------------------------------------------------
# IPC channel constants — shared across all layers
# ---------------------------------------------------------------------------
class IpcChannels:
    """Canonical channel names. Never hard-code strings elsewhere."""

    READ_FILE_BUFFER = "read-file-buffer"
    GET_APP_VERSION = "get-app-version"


# ---------------------------------------------------------------------------
# Payload shapes
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ReadFileRequest:
    """Payload sent from renderer → main for file reading."""

    file_path: str
    max_bytes: int | None = None


@dataclass(frozen=True)
class ReadFileResponse:
    """Payload returned from main → renderer after a successful read."""

    data: bytes
    size: int


@dataclass(frozen=True)
class IpcError:
    """Standard error shape for every failed IPC call."""

    code: str
    message: str
    detail: str | None = None


# ---------------------------------------------------------------------------
# Service-side protocol (backend / main-process adapters can implement this)
# ---------------------------------------------------------------------------
T = TypeVar("T")


@runtime_checkable
class IpcHandler(Protocol, Generic[T]):
    """Protocol for an IPC handler that can be registered in Electron main."""

    channel: str

    async def handle(self, payload: T) -> bytes:
        """Return the raw bytes that the preload will wrap in a Uint8Array."""
        ...


class FileBufferHandler(IpcHandler[ReadFileRequest]):
    """
    Concrete IPC handler for ``READ_FILE_BUFFER``.

    Accepts a ``ReadFileRequest`` and returns the file contents as ``bytes``.
    """

    channel = IpcChannels.READ_FILE_BUFFER

    def __init__(self, file_reader: "IFileReader") -> None:
        self._reader = file_reader

    async def handle(self, payload: ReadFileRequest) -> bytes:
        return await self._reader.read(payload.file_path, max_bytes=payload.max_bytes)


# ---------------------------------------------------------------------------
# Forward reference for the IFileReader protocol (same module, keep importable)
# ---------------------------------------------------------------------------
from app.services.file_reader_service import IFileReader  # noqa: E402
