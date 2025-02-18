import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from uuid import UUID


class LockManager:
    """Manages locks for concurrent account operations."""

    def __init__(self) -> None:
        self._locks: dict[str, asyncio.Lock] = {}
        self._lock = asyncio.Lock()

    async def _get_or_create_lock(self, lock_id: UUID) -> asyncio.Lock:
        """Get existing lock or create a new one if it doesn't exist."""
        lock_key = str(lock_id)
        async with self._lock:
            if lock_key not in self._locks:
                self._locks[lock_key] = asyncio.Lock()
            return self._locks[lock_key]

    @asynccontextmanager
    async def lock(self, lock_id: UUID) -> AsyncGenerator[None, Any]:
        """Context manager for account-specific locks."""
        lock = await self._get_or_create_lock(lock_id)
        try:
            await lock.acquire()
            yield
        finally:
            lock.release()
            # Clean up the lock if no one is waiting
            async with self._lock:
                lock_key = str(lock_id)
                if lock_key in self._locks and not self._locks[lock_key].locked():
                    del self._locks[lock_key]
