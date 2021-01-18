====================
Query Limiting
====================

.. _limiting_basics:

Basics
^^^^^^^^^^^

When using (public) SPARQL endpoints it is important to adhere to the usage policies defined by the providers. To ensure that you are not accidentally put too much strain on an endpoint this package automatically takes care of query limiting. The only thing you have to do is to correctly set up your :obj:`RemoteEndpoint <kgextension.sparql_helper.RemoteEndpoint>`.

.. _limiting_implementation:

Implementation
^^^^^^^^^^^^^^^^^

The first time you query a :obj:`RemoteEndpoint <kgextension.sparql_helper.RemoteEndpoint>` this package will create a ``rate_limits.db`` file. This file contains statistics about your past query activity and is created to make sure that you don't exceed the query limits, even if, for instance, you restart your Python session or re-initialize your :obj:`RemoteEndpoint <kgextension.sparql_helper.RemoteEndpoint>` object.

By default all :obj:`RemoteEndpoint <kgextension.sparql_helper.RemoteEndpoint>` objects will create the ``rate_limits.db`` file at your current working directory. However, this is just done in case there isn't already a ``rate_limits.db`` file present. All RemoteEndpoints can use the same file. However, if you want you can individually specify the path at which the file will be stored on a "per endpoint" basis. This is done via the ``persistence_file_path`` argument of the :obj:`RemoteEndpoint <kgextension.sparql_helper.RemoteEndpoint>` object, as shown in the example below.


.. code-block:: python

    from kgextension.sparql_helper import RemoteEndpoint

    DBpedia = RemoteEndpoint(url="http://dbpedia.org/sparql", persistence_file_path="/example_folder/rate_limits.db")

