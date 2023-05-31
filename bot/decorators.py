from functools import wraps
from time import time
import asyncio


def rate_limited(max_calls: int, time_period: int):

    def decorate(func):
        calls = 0
        last_reset = time()

        @wraps(func)
        async def rate_limited_func(*args, **kwargs):
            nonlocal calls
            nonlocal last_reset

            if time() - last_reset > time_period:
                calls = 0
                last_reset = time()

            if calls >= max_calls:
                return None
            calls += 1
            return await func(*args, **kwargs)

        return rate_limited_func

    return decorate


def send_limited():

    def decorate(func):
        calls_bot = 0

        @wraps(func)
        async def rate_limited_send(*args, **kwargs):
            nonlocal calls_bot
            if calls_bot > 90:
                await asyncio.sleep(15)
                calls_bot = 0
            calls_bot += 1
            return await func(*args, **kwargs)

        return rate_limited_send

    return decorate
