from setuptools import setup, find_packages

install_requires = ["docker-py==1.8.1", "progressbar2==3.5.0"]

setup(
    author = "Grahame Bowland",
    author_email = "grahame@angrygoats.net",
    description = "docker helper",
    license = "GPL3",
    keywords = "docker",
    url = "https://github.com/grahame/wrfy",
    name = "wrfy",
    version = "0.1.0",
    packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires = install_requires,
    entry_points = {
        "console_scripts": [
            "wrfy = wrfy.cli:main",
        ],
    }
)
