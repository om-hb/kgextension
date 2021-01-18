import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.rst").read_text()

# This call to setup() does all the work
setup(
    name="kgextension",
    version="0.0.1",
    description="The kgextension allows to access and use Linked Open Data to augment existing datasets. ",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://kgextension.readthedocs.io/en/latest/",
    author="KG Team Uni Mannheim",
    author_email="kgproject20@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords='knowledge graph, linked open data, sparql',
    packages=["kgextension"],
    include_package_data=True,
    install_requires=[
        "networkx",
        "numpy",
        "pandas",
        "info_gain",
        "scikit-learn",
        "tqdm",
        "lxml",
        "requests",
        "pyspotlight",
        "fuzzywuzzy",
        "strsimpy",
        "rdflib",
        "deckar01-ratelimit>=3.0.0",
        "SPARQLWrapper",
        "validators"],
    project_urls={  # Optional
        'Source': 'https://github.com/om-hb/kgextension',
        'Bug Reports': 'https://github.com/om-hb/kgextension/issues',
    }
)