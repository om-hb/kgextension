.. _endpoint-label:

====================
Endpoints
====================

Basics
^^^^^^^^^^^^^^^^^^^

To be able to work with this package properly, you first have to establish a connection to the SPARQL endpoint(s) you want extract desired the data from (except you just want to work with DBpedia, see `Using Preconfigured Endpoints`_).

SPARQL endpoints are implemented as :class:`kgextension.sparql_helper.Endpoint` objects.

.. note::
    For all methods in this package that need to access an Endpoint, the default Endpoint is set to be the DBpedia endpoint. This means, that if you just want to work with the DBPedia endpoint, *you don't have to take care of configuring or selecting an endpoint and can just use this package directly*.

Types of Endpoints
^^^^^^^^^^^^^^^^^^^

This package provides support for two kinds of Endpoints:

* **Remote Endpoints**: Remote Endpoint allow you to work with classic hosted SPARQL endpoints.
* **Local Endpoints**: Local Endpoints allow you to work with local RDF files as if they were hosted SPARQL endpoints.

Connecting to an Endpoint
^^^^^^^^^^^^^^^^^^^^^^^^^^

Using Preconfigured Endpoints
--------------------------------

For user convenience the package comes with a selection of preconfigured SPARQL endpoints, that are "ready to use" out of the box. This collection currently includes:

* `DBpedia <https://wiki.dbpedia.org/>`_: :class:`kgextension.endpoints.DBpedia` 
* `WikiData <https://www.wikidata.org/>`_: :class:`kgextension.endpoints.WikiData` 
* `EU Open Data Portal (EU ODP) <https://data.europa.eu/euodp/>`_: :class:`kgextension.endpoints.EUOpenData`  

These Endpoints can simply be imported when needed, as shown in the following example:

.. code-block:: python

    from kgextension.endpoints import DBpedia

The loaded Endpoint object can (:ref:`with the exception of the WikiData Endpoint <warning_wikidata_useragent>`) then be directly passed to the applicable functions.

.. _warning_wikidata_useragent:

.. warning::
    Wikidata requires a `custom (!) HTTP User-Agent header <https://meta.wikimedia.org/wiki/User-Agent_policy>`_ for all requests! You can set it as follows:

    .. code-block:: python

        from kgextension import __agent__
        from kgextension.endpoints import WikiData

        WikiData.agent = "CoolToolName/0.0 (https://example.org/cool-tool/; cool-tool@example.org) "+__agent__

Setup of own Endpoints
------------------------

Remote Endpoints
************************

To set up your own Remote Endpoint, you have to create an :obj:`kgextension.sparql_helper.RemoteEndpoint` object, as in the following example:

.. code-block:: python

    from kgextension.sparql_helper import RemoteEndpoint

    DBpedia = RemoteEndpoint(url = "http://dbpedia.org/sparql", timeout=120, requests_per_min=100*60, retries=10, page_size=10000)

.. note::
    Theoretically the only parameter needed to set up a RemoteEndpoint is the ``url`` parameter. However, it is important correctly set the remaining parameters, as they are needed for the automatic :doc:`tech_query_limiting` done by this package.

After the successful creation, the resulting RemoteEndpoint object can be passed to the applicable functions.

Local Endpoints
************************

Local Endpoints use the serializers provided by the `RDFLib package <https://rdflib.readthedocs.io/>`_ to parse the local RDF files. Therefore, multiple serialisation formats are supported (e.g. RDF/XML, N3 & Turtle). For more information regarding the supported formats, please reference the `RDFlib documentation <https://rdflib.readthedocs.io/en/stable/plugin_parsers.html>`_.

To set up your own Local Endpoint, you have to create an :class:`kgextension.sparql_helper.LocalEndpoint` object, as in the following example:

.. code-block:: python

    from kgextension.sparql_helper import LocalEndpoint

    Mondial = LocalEndpoint(file_path = "mondial-europe.rdf")

    Mondial.initialize()

Note the additional initialization call of the :meth:`initialize() <kgextension.sparql_helper.LocalEndpoint.initialize()>` method, which will load the provided data into local memory. As this can, depending on the size of the dataset, take quite some time and will potentially consume lots of memory, it is not performed automatically. After the initialization, the created LocalEndpoint object can then be passed to the applicable functions. 

If you want to remove the data from your local memory, you can call the :meth:`close() <kgextension.sparql_helper.LocalEndpoint.close()>` method.

.. code-block:: python

    Mondial.close()