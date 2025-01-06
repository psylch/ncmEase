from setuptools import setup, find_packages

setup(
    name="ncm_converter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pycryptodome>=3.9.0",
        "pytest>=6.0.0",
    ],
)