import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ModelProgrammer",
    version="0.0.3",
    author="Charlie Angela Mehlenbeck",
    author_email="charlie_inventor2003@yahoo.com",
    description="An experiment in AI terminal interaction.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/inventor2525/ModelProgrammer",
    packages=setuptools.find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "tiktoken",
        "PyQt5",
        "openai",
    ],
)
