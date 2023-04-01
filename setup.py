import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ModelProgrammer",
    version="0.0.1",
    author="Charlie Angela Mehlenbeck",
    author_email="charlie_inventor2003@yahoo.com",
    description="An experiment in AI terminal interaction.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/my-openai-project",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GPL-3.0 License",
        "Operating System :: Linux",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
    install_requires=[
        "asyncio",
        "os",
        "pty",
        "signal",
        "subprocess",
        "re",
        "tiktoken",
        "enum",
        "datetime",
        "sqlite3",
        "hashlib",
        "json",
        "PyQt5",
        "openai",
        "ast",
    ],
)
