import asyncio
from urllib.parse import urlparse

import aiohttp

from crawl import normalize_url, extract_page_data, PageData


class AsyncCrawler:
    def __init__(self, base_url: str, max_concurrency: int, max_pages: int) -> None:
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.page_data: dict[str, PageData] = {}
        self.visited: set[str] = set()
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks: set[asyncio.Task] = set()
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def add_page_visit(self, normalized_url: str) -> bool:
        async with self.lock:
            if self.should_stop:
                return False
            if normalized_url in self.visited:
                return False
            if len(self.visited) >= self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl.")
                return False
            self.visited.add(normalized_url)
            return True

    async def get_html(self, url: str) -> str:
        if self.session is None:
            raise RuntimeError("Session not started, use 'async with AsyncCrawler(...)'")

        async with self.session.get(
            url,
            headers={"User-Agent": "BootCrawler/1.0"},
            timeout=aiohttp.ClientTimeout(total=10),
        ) as resp:
            if resp.status >= 400:
                raise Exception(f"HTTP error {resp.status} for {url}")

            content_type = resp.headers.get("content-type", "")
            if "text/html" not in content_type:
                raise Exception(f"Non-HTML content type for {url}: {content_type}")

            return await resp.text()

    async def crawl_page(self, current_url: str) -> None:
        if self.should_stop:
            return

        if urlparse(current_url).netloc != self.base_domain:
            return

        normalized_url = normalize_url(current_url)
        if not await self.add_page_visit(normalized_url):
            return

        async with self.semaphore:
            print(f"Crawling: {current_url}")
            try:
                html = await self.get_html(current_url)
            except Exception as e:
                print(f"  Error fetching {current_url}: {e}")
                return
            data = extract_page_data(html, current_url)

        async with self.lock:
            self.page_data[normalized_url] = data

        if self.should_stop:
            return

        tasks = []
        for next_url in data["outgoing_links"]:
            task = asyncio.create_task(self.crawl_page(next_url))
            self.all_tasks.add(task)
            tasks.append(task)

        try:
            await asyncio.gather(*tasks)
        finally:
            for task in tasks:
                self.all_tasks.discard(task)

    async def crawl(self) -> dict[str, PageData]:
        await self.crawl_page(self.base_url)
        return self.page_data


async def crawl_site_async(
    base_url: str, max_concurrency: int, max_pages: int
) -> dict[str, PageData]:
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
        return await crawler.crawl()
