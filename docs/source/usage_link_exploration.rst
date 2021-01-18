.. _link-exploration-label:

====================
Link Exploration
====================

:class:`kgextension.link_exploration.link_explorer`

Overview
^^^^^^^^^^^^^^^^^^^^

The Link Exploration allows to extensively search the Linked Open Data (LOD)
Cloud for URIs connected to the original URIs  in the column obtained from
linking (see :ref:`linker-label`).
It follows the defined links starting from a base link to a certain number 
of hops. By default it follows the *owl:sameAs* predicate to hop from link to
link (it recursively applies the predicate on the newly obtained links). It
adds the discovered links as new columns to the dataframe. 

Consider as an example input the following toy example:
For a dataset entity "Berlin", the linker identified the corresponding
DBpedia URI "http://dbpedia.org/resource/Berlin".

+---------+------------------------------------+
| city    | uri                                |
+=========+====================================+
| Berlin  | http://dbpedia.org/resource/Berlin |
+---------+------------------------------------+

The link explorer can then be used to identify URIs belonging to
Berlin  as well and add them to the DataFrame:

+--------+------------------------------------+---------------------------------------+--------------------------------+----------------------------------------------+-----------------------------------------+
| city   | uri                                | http://cs.dbpedia.org                 | http://d-nb.info               | http://data.nytimes.com/16057429728088573361 | http://el.dbpedia.org                   | 
+========+====================================+=======================================+================================+==============================================+=========================================+
| Berlin | http://dbpedia.org/resource/Berlin | http://cs.dbpedia.org/resource/Berlín | http://d-nb.info/gnd/4005728-8 | http://data.nytimes.com/16057429728088573361 | http://el.dbpedia.org/resource/Βερολίνο |     
+--------+------------------------------------+---------------------------------------+--------------------------------+----------------------------------------------+-----------------------------------------+

The linker traverses through the different avaiable knowledge graphs as well as
through the different language versions of DBpedia. Note that this is a
shortened example: with a large number of hops specified, the link explorer can
find many more URIs.

_____________________________________

Parameters
^^^^^^^^^^^^^^^^^^^^

.. _Default:

Default Setting
***************

In its default version, the link explorer performs one hop
following the *owl:sameAs* predicate without filtering.

.. code-block:: python

    df_link_explored = link_explorer(
        df, base_link_column, number_of_hops = 1, 
        links_to_follow = ["owl:sameAs"], 
        lod_sources = [], exclude_sources = []
    )


_____________________________________

.. _Number-of-hops:

Number of Hops
***************

In order to generate more URI columns, the number of hops can be increased to
any positive integer.
This means that if we set the number of hops to two, we follow e.g. the link of
the first hop to the French wikipedia URI of Berlin,
http://fr.dbpedia.org/resource/Berlin, and then follow
all other *owl:sameAs* links from this French site again. If the number of hops
were three, and we followed among all links of the French site also the one to
the Greek site, we would again hop on all other links occurring on the Greek
dbpedia URI of Berlin.

.. code-block:: python

    df_link_explored = link_explorer(
        df, base_link_column='uri', number_of_hops = 2
    )

.. _warning_exponential_link_creation:
.. warning::
    Increasing the number of hops by one integer point, e.g. from 2 to 3, does
    not imply that three columns with URIs will be added, but that from the
    first resource all links will be followed, which in turn will all be the
    starting points for the next hop and so on. Thus, even a small number of
    hops is approximately exponential in time.

_____________________________________

.. _Links-to-follow:

Links to Follow
***************

The link explorer can follow arbitrary links and also multiple at the same
time.
In this example, we add *rdfs:seeAlso* to the list of links to follow:

.. code-block:: python

    df_link_explored = link_explorer(
        df, base_link_column='uri', 
        links_to_follow=["owl:sameAs","rdfs:seeAlso"]
    )

For the http://dbpedia.org/resource/Berlin, now URIs that are connected to it
via the *rdfs:seeAlso* property are added as well, e.g.
http://dbpedia.org/resource/Sister_city. 


_____________________________________

.. _Include-sources:

Include Sources
***************
Since the process of hopping from link to link can be quite randomly, it is
possible to specify sources the results should be limited two, e.g. certain
knowledge graphs. Use strings or regular expressions to define, which sources
to include. In the following example, the links are limited to the
*nytimes* and *geonames* knowledge graphs.

.. code-block:: python

    df_link_explored = link_explorer(
        df, base_link_column='uri', 
        lod_sources=["nytimes","geonames"]
    )

+--------+------------------------------------+----------------------------------------------+-----------------------------------------------+---------------------------------+
| city   | uri                                | http://data.nytimes.com/16057429728088573361 | http://data.nytimes.com/N50987186835223032381 | http://sws.geonames.org/2950157 |
+========+====================================+==============================================+===============================================+=================================+
| Berlin | http://dbpedia.org/resource/Berlin | http://data.nytimes.com/16057429728088573361 | http://data.nytimes.com/N50987186835223032381 | http://sws.geonames.org/2950157 |
+--------+------------------------------------+----------------------------------------------+-----------------------------------------------+---------------------------------+


_____________________________________

.. _Exclude-sources:

Exclude Sources
***************

In contrast to specifying certain sources, it is also possible to define
knowledge graphs to be absent from the newly generated URIs. Use strings or
regular expressions to define, which sources to exclude.
In the following example, URIs from dbpedia will not be allowed.

.. code-block:: python

    df_link_explored = link_explorer(
        df, base_link_column='uri', 
        exclude_sources=["dbpedia"]
    )
