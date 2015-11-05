#!/bin/env python3
# vim: expandtab shiftwidth=4 softtabstop=4 tabstop=17 filetype=python :
"""
Upload a set of .csr files to a caramel endpoint. Used for some minor
benchmarking and to populate things"""

import asyncio
import aiohttp

ENDPOINT = "devnull-as-a-service.com"
ENDPOINT = "https://modio.se/"
sem = asyncio.Semaphore(60)

@asyncio.coroutine
def fetch_page(url, placeholder=None):
    with (yield from sem):
        response = yield from aiohttp.request('HEAD', url)
        data = yield from response.read_and_close()

@asyncio.coroutine
def fetch_session(url, session):
    with (yield from sem):
        response = yield from session.request('HEAD', url)
        data = yield from response.read()

@asyncio.coroutine
def main():
    session = aiohttp.ClientSession()
    urls = [ENDPOINT] * 100000
    coro = [asyncio.Task(fetch_session(url, session)) for url in urls]
    yield from asyncio.gather(*coro)
    session.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    session = aiohttp.ClientSession()
    loop.run_until_complete(asyncio.wait([fetch_page(ENDPOINT),
                             fetch_session(ENDPOINT, session)]))
    session.close()
    loop.run_until_complete(main())
