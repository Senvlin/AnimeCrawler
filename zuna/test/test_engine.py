import asyncio
import time
import unittest

from zuna.src.engine import Engine


async def _run(engine, root_url):
    try:
        t1 = time.perf_counter()
        await engine.init(root_url)
        t2 = time.perf_counter()
        print(f"init time: {(t2 - t1):.2f} s")
    finally:
        await engine.spider.request_session.close()


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.root_url = "https://shoubozhan.com/vodplay/125758-1-1.html"
        self.html_str = "<html><body><h1>Test</h1></body></html>"

        self.engine = Engine()

    def test_run_without_crawl(self):
        asyncio.run(_run(self.engine, self.root_url))


if __name__ == "__main__":
    unittest.main(buffer=True)
