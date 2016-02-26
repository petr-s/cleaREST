from setuptools import setup

setup(
    name="cleaREST",
    version="0.0.1",
    author="Petr Skramovsky",
    author_email="petr.skramovsky@gmail.com",
    description="Light-weight Python framework for building REST apis.",
    license="MIT",
    keywords="rest api framework json xml",
    url="https://github.com/petr-s/cleaREST",
    packages=["clearest", "tests"],
    test_suite="tests",
    long_description=open("README.rst").read(),
    classifiers=[
        "Development Status :: 1 - Planning",
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
