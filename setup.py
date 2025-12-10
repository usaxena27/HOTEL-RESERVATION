from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="HOTEL-RESERVATION",
    version="0.1",
    author="UTKARSH",
    packages=find_packages(),
    install_requires=requirements,
)