import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="AnimeCrawler",
    version="v0.1.0",
    author="Senvlin",
    author_email="2994515402@qq.com",
    description="test",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Senvlin/AnimeCrawler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'ruia==0.8.5',
        'tqdm==4.65.0',
        'aiofiles==23.1.0',
    ],
    python_requires='>=3.8',
)
