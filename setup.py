from setuptools import setup

import clearest

setup(
    name="cleaREST",
    version=clearest.__version__,
    author=clearest.__author__,
    author_email=clearest.__contact__,
    description="Light-weight Python framework for building REST APIs.",
    license="MIT",
    keywords="rest api framework json xml",
    url=clearest.__homepage__,
    packages=["clearest", "tests", "sample"],
    test_suite="tests",
    long_description=open("README.rst").read(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
    ],
)
