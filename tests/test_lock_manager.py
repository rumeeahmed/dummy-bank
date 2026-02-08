import asyncio
from uuid import UUID

import pytest

from dummy_bank.api.lock_manager import LockManager


class TestLockManager:
    @pytest.mark.asyncio
    async def test_lock_creation_and_reuse(
        self, lock_id: UUID, lock_manager: LockManager
    ) -> None:
        # Get the lock for the first time
        lock1 = await lock_manager._get_or_create_lock(lock_id)
        # Get the lock for the second time (should be the same)
        lock2 = await lock_manager._get_or_create_lock(lock_id)

        assert lock1 is lock2
        assert str(lock_id) in lock_manager._locks

    @pytest.mark.asyncio
    async def test_lock_context_manager_acquires_and_releases(
        self, lock_id: UUID, lock_manager: LockManager
    ) -> None:
        async with lock_manager.lock(lock_id):
            # Lock should be acquired
            lock = await lock_manager._get_or_create_lock(lock_id)
            assert lock.locked()

        # After the context, lock should be released
        lock = await lock_manager._get_or_create_lock(lock_id)
        assert not lock.locked()

    @pytest.mark.asyncio
    async def test_lock_cleanup(self, lock_id: UUID, lock_manager: LockManager) -> None:
        async with lock_manager.lock(lock_id):
            pass  # Lock is acquired and released here

        # The lock should be cleaned up after being released
        await asyncio.sleep(1)  # Give event loop a chance to clean up
        assert str(lock_id) not in lock_manager._locks
