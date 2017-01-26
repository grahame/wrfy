import sys
from setuptools import setup, find_packages

if not sys.version_info[0] == 3:
    sys.exit("Sorry, this is a Python 3 utility")

install_requires = ["docker==2.0.2", "progressbar2==3.5.0"]

setup(
    author="Grahame Bowland",
    author_email="grahame@angrygoats.net",
    description="docker helper",
    license="GPL3",
    keywords="docker",
    url="https://github.com/grahame/wrfy",
    name="wrfy",
    version="0.6.0",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "wrfy=wrfy.cli:main",
        ],
    }
)
