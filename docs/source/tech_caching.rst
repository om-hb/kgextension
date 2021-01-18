====================
Caching
====================

.. _cache_basics:

Basics
^^^^^^^^^^^

This package automatically caches the results of all queries made to external resources. This includes the results of:

* SPARQL queries (via the :meth:`endpoint_wrapper() <kgextension.sparql_helper.endpoint_wrapper()>` method).
* URI querying (via the :meth:`uri_querier() <kgextension.uri_helper.uri_querier()>` method).
* DBpedia Lookup Linker requests (via the :meth:`dll_query_resolver() <kgextension.linking_helper.dll_query_resolver()>` method).
* DBpedia Spotlight requests (via the :meth:`spotlight_uri_extractor() <kgextension.linking_helper.spotlight_uri_extractor()>` method).
* Checks for URL availability (via the :meth:`url_exists() < kgextension.utilities_helper.url_exists()>` method).´

.. note::
   As of now the size of the cache is and can not be limited. If you run into issues with regards of memory usage, try :ref:`to clear the cache <clearing_cache>`.

.. _cache_usage:

Usage
^^^^^^^^^^^

.. _disabling_cache:

Disabling Caching
-----------------------

Caching can be manually disabling on a "per call" level by setting the ``caching`` parameter of a cached method to **False**, as shown in the example below.

.. code-block:: python

    df_linked = label_linker(df, column='author', caching=False)

At the moment it is not possible to easily disable caching for all methods at once.

.. _checking_cache:

Checking the Cache Status
--------------------------

To check the status of the cache, call the :meth:`show_cache_info() <kgextension.caching_helper.show_cache_info()>` method, as shown in the example below.

.. code-block:: python

    from kgextension.caching_helper import show_cache_info

    show_cache_info()

.. _clearing_cache:

Clearing the Cache
-----------------------

To clear the cache, call the :meth:`clear_cache() <kgextension.caching_helper.clear_cache()>` method, as shown in the example below.

.. code-block:: python

    from kgextension.caching_helper import clear_cache

    clear_cache()

