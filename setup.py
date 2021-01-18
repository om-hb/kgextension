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
    long_description_content_type="text/x-rst",
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
        'chardet==4.0.0',
        'deckar01-ratelimit==3.0.1',
        'decorator==4.4.2',
        'featuretools==0.7.1',
        'fuzzywuzzy==0.18.0',
        'idna==2.10',
        'info-gain==1.0.1',
        'isodate==0.6.0',
        'lxml==4.6.2',
        'networkx==2.5',
        'numpy==1.19.5',
        'pandas==1.2.0',
        'pyparsing==2.4.7',
        'pyspotlight==0.7.2',
        'python-dateutil==2.8.1',
        'PyYAML==5.3.1',
        'rdflib==5.0.0',
        'requests==2.25.1',
        'scikit-learn==0.20.3',
        'SPARQLWrapper==1.8.5',
        'strsimpy==0.2.0',
        'tqdm==4.31.1',
        'urllib3==1.26.2',
        'validators==0.18.2',
        ],
    project_urls={  # Optional
        'Source': 'https://github.com/om-hb/kgextension',
        'Bug Reports': 'https://github.com/om-hb/kgextension/issues',
    }
)
