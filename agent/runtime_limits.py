# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass(slots=True)
class BatchRuntimeLimits:
    local_work_semaphore: asyncio.Semaphore | None = None

    @asynccontextmanager
    async def local_work(self) -> AsyncIterator[None]:
        if self.local_work_semaphore is None:
            yield
            return
        async with self.local_work_semaphore:
            yield


@asynccontextmanager
async def local_work_slot(limits: BatchRuntimeLimits | None) -> AsyncIterator[None]:
    if limits is None:
        yield
        return
    async with limits.local_work():
        yield
