from setuptools import setup, find_packages

setup(
    name="lionweb-python",
    version="0.1.0",
    author="Federico Tomassetti",
    author_email="info@lionweb.io",
    description="Python Bindings for LionWeb",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LionWeb-io/lionweb-python",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
)