import asyncio

from zuna.src.engine import Engine

engine = Engine()


async def main(root_url):
    await engine.run(root_url)


if __name__ == "__main__":
    asyncio.run(main("https://shoubozhan.com/vodplay/125758-1-1.html"))
