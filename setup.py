import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="doreah",
    version="0.6.1",
    author="Johannes Krattenmacher",
    author_email="python@krateng.dev",
    description="Small toolkit of utilities for python projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/krateng/doreah",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
