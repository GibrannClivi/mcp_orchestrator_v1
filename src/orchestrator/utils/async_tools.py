"""
Async utility functions for wrapping blocking calls.
"""
import asyncio
from typing import Callable, Any

async def run_in_thread(func: Callable, *args, **kwargs) -> Any:
    return await asyncio.to_thread(func, *args, **kwargs)
