import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="AnimeCrawler",
    version="v0.2.1",
    author="Senvlin",
    author_email="2994515402@qq.com",
    description="一个可免费下载动漫的爬虫",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Senvlin/AnimeCrawler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['ruia', 'tqdm', 'aiofiles', 'wheel'],
    entry_points={
        'console_scripts': [
            'animecrawler = AnimeCrawler.command.run:main',
        ],
    },
    python_requires='>=3.8',
)
