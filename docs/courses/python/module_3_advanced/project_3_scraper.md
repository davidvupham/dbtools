# Project 3: High-Concurrency Web Scraper

**Goal**: Fetch data from multiple URLs simultaneously to demonstrate concurrency.

## Learning Objectives

* Asyncio (`async`/`await`)
* Threading (for I/O bound tasks)
* Generators
* Performance Measurement

## Requirements

1. **Target**: Use a placeholder API like `https://jsonplaceholder.typicode.com/posts/{id}`.
2. **Sequential Version**: Fetch 50 posts one by one. Measure time.
3. **Async Version**: Fetch 50 posts concurrently using `aiohttp` (or `httpx`) and `asyncio.gather`. Measure time.
4. **Data Processing**: Use a generator to yield posts as they are fetched.

## Challenge

Implement a "Throttle" to limit requests to 5 per second using an `asyncio.Semaphore`.
