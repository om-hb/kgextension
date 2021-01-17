.. _linker-label:

====================
Linking
====================

- pattern_linker_.
- label_linker_.
- dbpedia_lookup_linker_.
- dbpedia_spotlight_linker_.
- sameas_linker_.

Overview
^^^^^^^^^^^^^^^^^^^^

The Linking functions connect instances in a dataset to 
the respective URIs of a knowledge graph. They create 
one or more additional column(s) in the pandas DataFrame holding the URIS.
These URIs can be later on used to generate additional features, as explained
in :doc:`usage_generators`.


The input to the linking function is a :class:`pandas.DataFrame.column` with entities for which
additional information is desired. In the following example case additional information about
book authors. 

.. code-block:: python

    import pandas

    df = pd.DataFrame({
        'author': ['Stephen King', 'Joanne K. Rowling', 'Dan Brown']
    })


+-------------------+
| author            | 
+===================+
| Stephen King      | 
+-------------------+
| Joanne K. Rowling | 
+-------------------+
| Dan Brown         | 
+-------------------+ 

The linking functions connects the
entity, here the author, to its knowledge graph URI. The URIs appear in a newly
created column in the DataFrame.

+-------------------+-------------------------------------------+
| author            | new_link                                  |
+===================+===========================================+
| Stephen King      | http://dbpedia.org/resource/Stephen_King  |
+-------------------+-------------------------------------------+
| Joanne K. Rowling | http://dbpedia.org/resource/J._K._Rowling |
+-------------------+-------------------------------------------+
| Dan Brown         | http://dbpedia.org/resource/Dan_Brown     |
+-------------------+-------------------------------------------+ 

_____________________________________

.. _pattern_linker:

pattern_linker
^^^^^^^^^^^^^^^^^^^^
:class:`kgextension.linking.pattern_linker`

The pattern linker takes the strings from the column that contains the 
entities to be linked and attaches them to a base link. For
example, the base_url "www.examplegraph.com/resource" and the entity "New York
City" are combined to the URI "www.examplegraph.com/resource/New_York_City".
The option url_encoding automatically applies URL encoding. The
option DBpedia_link_format enables the conversion to the format that Dbpedia
links are created in.


.. code-block:: python

    from kgextension.endpoints import WikiData

    df_pattern_linked = pattern_linker(
        df, column='author', new_attribute_name="new_link",  
        base_url="http://dbpedia.org/resource/", url_encoding=True, 
        DBpedia_link_format=True
    )


+-------------------+-----------------------------------------------+
| author            | new_link                                      |
+===================+===============================================+
| Stephen King      | http://dbpedia.org/resource/Stephen_King      |
+-------------------+-----------------------------------------------+
| Joanne K. Rowling | http://dbpedia.org/resource/Joanne_K._Rowling |
+-------------------+-----------------------------------------------+
| Dan Brown         | http://dbpedia.org/resource/Dan_Brown         |
+-------------------+-----------------------------------------------+ 

:Advantage: fast
:Disadvantage: correctly spelled data required

_____________________________________

.. _label_linker:

label_linker
^^^^^^^^^^^^^^^^^^^^
:class:`kgextension.linking.label_linker`

The label linker generates URIs by running a Sparql Query with the entity
from the column and a label predicate, by default *rdfs:label*. This query is 
passed to the selected endpoint. 

Default
********

.. code-block:: python

    df_label_linked = label_linker(
        df, column='author', new_attribute_name="new_link", 
        endpoint=DBpedia, result_filter=None, language="en", max_hits=1, 
        label_property="rdfs:label"
    )


+-------------------+---------------------------------------------------+
| author            | new_link_1                                        |
+===================+===================================================+
| Stephen King      | http://dbpedia.org/resource/Category:Stephen_King |
+-------------------+---------------------------------------------------+
| Joanne K. Rowling | http://dbpedia.org/resource/Joanne_K._Rowling     |
+-------------------+---------------------------------------------------+
| Dan Brown         | http://dbpedia.org/resource/Category:Dan_Brown    |
+-------------------+---------------------------------------------------+ 

Language
********

By setting the language tag to a different language, e.g. Spanish, the words 
are generally translated to the English
URI with the same meaning, whereas the English language setting keeps the
original meaning.

+-------------------+--------------------------------------+
| spanish_word      | new_link (language='es')             |
+===================+======================================+
| Prado             | http://dbpedia.org/resource/Meadow   |
+-------------------+--------------------------------------+  
| Leche             | http://dbpedia.org/resource/Milk     |
+-------------------+--------------------------------------+  
| Medellín          | http://dbpedia.org/resource/Medellin |
+-------------------+--------------------------------------+ 


+-------------------+--------------------------------------+
| spanish_word      | new_link (language='en')             |
+===================+======================================+
| Prado             | http://dbpedia.org/resource/Prado    |
+-------------------+--------------------------------------+  
| Leche             | http://dbpedia.org/resource/Leche    |
+-------------------+--------------------------------------+  
| Medellín          | http://dbpedia.org/resource/Medellin |
+-------------------+--------------------------------------+ 


Number of Links
*****************

By increasing the number of max_hits, several URI - columns are created
whenever at least one of the entities has more than one label.

.. code-block:: python

    df_label_linked = label_linker(
        df, column='identity', max_hits=2
    )


+-----------+--------------------------------------------+--------------------------------------------+
| identity  | new_link_1                                 | new_link_2                                 |
+===========+============================================+============================================+
| President | http://dbpedia.org/property/president      | http://dbpedia.org/resource/President      |
+-----------+--------------------------------------------+--------------------------------------------+    
| Aruba     | http://dbpedia.org/resource/Category:Aruba | http://dbpedia.org/resource/Aruba          |
+-----------+--------------------------------------------+--------------------------------------------+    
| Apple     | http://dbpedia.org/resource/Category:Apple | http://dbpedia.org/resource/Apple          |
+-----------+--------------------------------------------+--------------------------------------------+  
| Paris     | http://dbpedia.org/resource/Category:Paris | http://dbpedia.org/resource/Paris          |
+-----------+--------------------------------------------+--------------------------------------------+


Endpoint
*********

By changing the endpoint, the resources are connected to another knowledge
graph. Some endpoints are already predefined, such as DBpedia, WikiData and
EUOpenData (EU Open Data Portal). For more information on endpoints, see
:ref:`endpoint-label`. 

.. code-block:: python

    from kgextension.endpoints import WikiData

    df_label_linked = label_linker(
        df, column='identity', endpoint=WikiData
    )

+-------------------+-----------------------------------------+
| identity          | new_link_1                              | 
+===================+=========================================+
| President         | http://www.wikidata.org/entity/Q493203  | 
+-------------------+-----------------------------------------+     
| Apple             | http://www.wikidata.org/entity/Q213710  |
+-------------------+-----------------------------------------+  
| Benjamin Franklin | http://www.wikidata.org/entity/Q1218541 |          
+-------------------+-----------------------------------------+

Label Property
***************

Label Properties other than rdfs:label can lead to URI attributions. Consider
for example the property foaf:name in the case of named entities.

.. code-block:: python

    df_label_linked = label_linker(
        df, column='identity', label_property='foaf:name'
    )

+----------------------+--------------------------------------------------+
| identity             | new_link_1                                       | 
+======================+==================================================+
| Titanic              | http://dbpedia.org/resource/Titanic_(1915_film)  | 
+----------------------+--------------------------------------------------+     
| Marie Curie          | http://dbpedia.org/resource/Marie_Curie          |
+----------------------+--------------------------------------------------+  
| Florence Nightingale | http://dbpedia.org/resource/Florence_Nightingale |          
+----------------------+--------------------------------------------------+

_____________________________________

.. _dbpedia_lookup_linker:

dbpedia_lookup_linker
^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
:class:`kgextension.linking.lookup_linker`

This linker accesses the DBpedia Lookup web service that can be used to look up
DBpedia URIs by related keywords. Related means that either the label of a
resource matches, or an anchor text that was frequently used in Wikipedia to
refer to a specific resource matches (for example the resource
http://dbpedia.org/resource/United_States can be looked up by the string
"USA"). The results are ranked by the number of inlinks pointing from other
Wikipedia pages at a result page.  
See the `DBpediaLookupAPI
<https://github.com/dbpedia/lookup/>`_.

Default
********

.. code-block:: python

    df_lookup_linked = dbpedia_lookup_linker(
        df, column="identity", new_attribute_name="new_link", 
        query_class="", max_hits=1, lookup_api="KeywordSearch"
    )

+-------------------------+-------------------------------------------+
| identity                | new_link                                  | 
+=========================+===========================================+
| Germany                 | http://dbpedia.org/resource/Germany       | 
+-------------------------+-------------------------------------------+     
| Italy                   | http://dbpedia.org/resource/Italy         |
+-------------------------+-------------------------------------------+  
| United States of America| http://dbpedia.org/resource/United_States |          
+-------------------------+-------------------------------------------+

Number of Links
*****************

Because the Lookup API also finds URIs of related concepts, many different URIs
can be found per entity, as can be seen in the following example. While the
first link has the strongest connection to the original string, each new link
deviates more from the original meaning but is related to it. 

.. code-block:: python

    df_lookup_linked = dbpedia_lookup_linker(
        df, column="identity", max_hits=5
    )

+-------------------------+-------------------------------------------+----------------------------------------------------------+---------------------------------------------------+--------------------------------------------------------+-----------------------------------------------------+
| identity                | new_link_1                                | new_link_2                                               | new_link_3                                        | new_link_4                                             | new_link_5                                          |
+=========================+===========================================+==========================================================+===================================================+========================================================+=====================================================+
| Germany                 | http://dbpedia.org/resource/Germany       | http://dbpedia.org/resource/Berlin                       | http://dbpedia.org/resource/Nazi_Germany          | http://dbpedia.org/resource/Munich                     | http://dbpedia.org/resource/Hamburg                 |     
+-------------------------+-------------------------------------------+----------------------------------------------------------+---------------------------------------------------+--------------------------------------------------------+-----------------------------------------------------+      
| Italy                   | http://dbpedia.org/resource/Italy         | http://dbpedia.org/resource/Rome                         | http://dbpedia.org/resource/Milan                 | http://dbpedia.org/resource/Venice                     | http://dbpedia.org/resource/Florence                |   
+-------------------------+-------------------------------------------+----------------------------------------------------------+---------------------------------------------------+--------------------------------------------------------+-----------------------------------------------------+      
| United States of America| http://dbpedia.org/resource/United_States | http://dbpedia.org/resource/National_Academy_of_Sciences | http://dbpedia.org/resource/United_States_Capitol | http://dbpedia.org/resource/Southeastern_United_States | http://dbpedia.org/resource/M-55_(Michigan_highway) |     
+-------------------------+-------------------------------------------+----------------------------------------------------------+---------------------------------------------------+--------------------------------------------------------+-----------------------------------------------------+    


Query Class
*************
A DBpedia class from the `DBpedia Ontology
<https://wiki.dbpedia.org/services-resources/ontology>`_ that the  
results should fall into (without prefix, e.g., dbo:place as place) can be
specified. 

.. code-block:: python

    df_lookup_linked = dbpedia_lookup_linker(
        df, column="car", query_class='Automobile'
    )

+-------------------+---------------------------------------------------+
| car               | new_link                                          | 
+===================+===================================================+
| Audi A8           | http://dbpedia.org/resource/Audi_A8               | 
+-------------------+---------------------------------------------------+     
| Porsche Cayenne   | http://dbpedia.org/resource/Porsche_Cayenne       |
+-------------------+---------------------------------------------------+  
| Tesla Model S     | http://dbpedia.org/resource/United_States         |          
+-------------------+---------------------------------------------------+
| Mercedes S Klasse | http://dbpedia.org/resource/Mercedes-Benz_S-Class |          
+-------------------+---------------------------------------------------+

Search Modus: Prefix Search
*****************************

Additional to the default case of a Keyword Search, there is the option to
conduct a prefix search that can be used to implement autocomplete input boxes.

.. code-block:: python

    df_lookup_linked = dbpedia_lookup_linker(
        df, column="president", lookup_api="PrefixSearch"
    )

+-----------+--------------------------------------------+
| president | new_link                                   | 
+===========+============================================+
| Bill C    | http://dbpedia.org/resource/Bill_Clinton   | 
+-----------+--------------------------------------------+     
| George B  | http://dbpedia.org/resource/George_W._Bush |
+-----------+--------------------------------------------+  
| Barac     | http://dbpedia.org/resource/Barack_Obama   |          
+-----------+--------------------------------------------+
| Donal     | http://dbpedia.org/resource/Donald_Trump   |          
+-----------+--------------------------------------------+


:Advantage: typo-insensitive
:Disadvantage: DBpedia-specific

_____________________________________

.. _dbpedia_spotlight_linker:

dbpedia_spotlight_linker
^^^^^^^^^^^^^^^^^^^^^^^^^
:class:`kgextension.linking.dbpedia_spotlight_linker`

This linker connects to the annotation tool `DBpediaSpotlight
<https://www.dbpedia-spotlight.org/>`_.
With the use of named entity recognition and related methods it identifies DBpedia resources from a
text and allows to filter the results with confidence, support and similarity
score measures.

Default
********

.. code-block:: python

    df_spotlight_linked = dbpedia_spotlight_linker(
        df, column, new_attribute_name="new_link", max_hits=1, 
        language="en", selection="first", confidence=0.3, support=5, 
        min_similarity_score=0.5
    )

+-----------+---------------------------------------+
| animal    | new_link                              | 
+===========+=======================================+
| Anaconda  | http://dbpedia.org/resource/Anaconda  | 
+-----------+---------------------------------------+     
| Bonobo    | http://dbpedia.org/resource/Bonobo    |
+-----------+---------------------------------------+  
| Jellyfish | http://dbpedia.org/resource/Jellyfish |          
+-----------+---------------------------------------+
| Eagle     | http://dbpedia.org/resource/Eagle     |          
+-----------+---------------------------------------+

Number of Links and Selection Method
**************************************

When more than one entity can be identified from the column, the ordering of
them is determined by the selection method. Three are available: the default is
*first*, i.e. the URIs are ordered in accordance with their occurrence.
*support* orders the results by descending support and *similarityScore* by
descending similarity score.

The following example shows how the ordering of the URI columns can change with
the chosen selection method.

selection='first'
++++++++++++++++++

.. code-block:: python

    df_spotlight_linked = dbpedia_spotlight_linker(
        df, 'sentence', max_hits=5, selection="first", 
    )

+----------------------------------------------------------+--------------------------------------+---------------------------------------+-----------------------------------------+----------------------------------------+-----------------------------------+
| sentence                                                 | new_link_1                           | new_link_2                            | new_link_3                              | new_link_4                             | new_link_5                        |
+==========================================================+======================================+=======================================+=========================================+========================================+===================================+
| The Anaconda hides behind a cactus to catch the mouse.   | http://dbpedia.org/resource/Anaconda | http://dbpedia.org/resource/Bird_hide | http://dbpedia.org/resource/Cactus      | http://dbpedia.org/resource/Caught     | http://dbpedia.org/resource/Mouse |     
+----------------------------------------------------------+--------------------------------------+---------------------------------------+-----------------------------------------+----------------------------------------+-----------------------------------+      
| The Bonobo awaits the gorillas to visit the rain forest. | http://dbpedia.org/resource/Bonobo   | http://dbpedia.org/resource/Gorilla   | http://dbpedia.org/resource/State_visit | http://dbpedia.org/resource/Rainforest | NaN                               |   
+----------------------------------------------------------+--------------------------------------+---------------------------------------+-----------------------------------------+----------------------------------------+-----------------------------------+      

selection='support'
++++++++++++++++++++++++++

.. code-block:: python

    df_spotlight_linked = dbpedia_spotlight_linker(
        df, 'sentence', max_hits=5, selection="support", 
    )

+----------------------------------------------------------+----------------------------------------+-------------------------------------+-----------------------------------------+--------------------------------------+---------------------------------------+
| sentence                                                 | new_link_1                             | new_link_2                          | new_link_3                              | new_link_4                           | new_link_5                            |
+==========================================================+========================================+=====================================+=========================================+======================================+=======================================+
| The Anaconda hides behind a cactus to catch the mouse.   | http://dbpedia.org/resource/Mouse	    | http://dbpedia.org/resource/Cactus  | http://dbpedia.org/resource/Caught	    | http://dbpedia.org/resource/Anaconda | http://dbpedia.org/resource/Bird_hide |     
+----------------------------------------------------------+----------------------------------------+-------------------------------------+-----------------------------------------+--------------------------------------+---------------------------------------+      
| The Bonobo awaits the gorillas to visit the rain forest. | http://dbpedia.org/resource/Rainforest | http://dbpedia.org/resource/Gorilla | http://dbpedia.org/resource/State_visit | http://dbpedia.org/resource/Bonobo   | NaN                                   |   
+----------------------------------------------------------+----------------------------------------+-------------------------------------+-----------------------------------------+--------------------------------------+---------------------------------------+      

selection='similarityScore'
++++++++++++++++++++++++++++

.. code-block:: python

    df_spotlight_linked = dbpedia_spotlight_linker(
        df, 'sentence', max_hits=5, selection="similarityScore", 
    )

+----------------------------------------------------------+------------------------------------+----------------------------------------+--------------------------------------+-----------------------------------------+---------------------------------------+
| sentence                                                 | new_link_1                         | new_link_2                             | new_link_3                           | new_link_4                              | new_link_5                            |
+==========================================================+====================================+========================================+======================================+=========================================+=======================================+
| The Anaconda hides behind a cactus to catch the mouse.   | http://dbpedia.org/resource/Cactus	| http://dbpedia.org/resource/Caught     | http://dbpedia.org/resource/Anaconda	| http://dbpedia.org/resource/Mouse       | http://dbpedia.org/resource/Bird_hide |     
+----------------------------------------------------------+------------------------------------+----------------------------------------+--------------------------------------+-----------------------------------------+---------------------------------------+      
| The Bonobo awaits the gorillas to visit the rain forest. | http://dbpedia.org/resource/Bonobo | http://dbpedia.org/resource/Rainforest | http://dbpedia.org/resource/Gorilla  | http://dbpedia.org/resource/State_visit | NaN                                   |   
+----------------------------------------------------------+------------------------------------+----------------------------------------+--------------------------------------+-----------------------------------------+---------------------------------------+      


Filtering
**************************************

There are three different thresholds to set to filter results: confidence,
support and minimum similarity score. By increasing the thresholds, the
selection of URIs has to fulfill to the stricter standards. The following two
examples show the same inputs with different filter settings.

*Laissez-faire* Filtering
++++++++++++++++++++++++++++

.. code-block:: python

    df_spotlight_linked = dbpedia_spotlight_linker(
        df, 'sentence', confidence=0, support=0, min_similarity_score=0, max_hits=4
    )

+----------------------------------------------------+--------------------------------------------+-------------------------------------------+-----------------------------------------------+---------------------------------------+
| sentence                                           | new_link_1                                 | new_link_2                                | new_link_3                                    | new_link_4                            | 
+====================================================+============================================+===========================================+===============================================+=======================================+
| The eucalyptus tree grows in Australia.            | http://dbpedia.org/resource/The_Eucalyptus | http://dbpedia.org/resource/Eucalyptus    | http://dbpedia.org/resource/Population_growth | http://dbpedia.org/resource/Australia |     
+----------------------------------------------------+--------------------------------------------+-------------------------------------------+-----------------------------------------------+---------------------------------------+     
| Anna goes shopping in the mall of Western Chicago. | http://dbpedia.org/resource/Anna_Windass   | http://dbpedia.org/resource/Shopping_mall | http://dbpedia.org/resource/Western_world     | http://dbpedia.org/resource/Chicago   |   
+----------------------------------------------------+--------------------------------------------+-------------------------------------------+-----------------------------------------------+---------------------------------------+ 

In this case, the loose filtering rules allow non-sensical URIs, such as
http://dbpedia.org/resource/Anna_Windass and
http://dbpedia.org/resource/Population_growth to appear.

Strict Filtering
++++++++++++++++++++++++++++

.. code-block:: python

    df_spotlight_linked = dbpedia_spotlight_linker(
        df, 'sentence', confidence=0.9, support=7, min_similarity_score=0.9, max_hits=4
    )

+----------------------------------------------------+---------------------------------------+
| sentence                                           | new_link                              |                                                            
+====================================================+=======================================+
| The eucalyptus tree grows in Australia.            | http://dbpedia.org/resource/Australia |  
+----------------------------------------------------+---------------------------------------+
| Anna goes shopping in the mall of Western Chicago. | http://dbpedia.org/resource/Chicago   | 
+----------------------------------------------------+---------------------------------------+ 

In this case, the filter is very strict; while both
http://dbpedia.org/resource/Australia and http://dbpedia.org/resource/Chicago
are correct, other URIs that are correct as well such as
http://dbpedia.org/resource/Eucalyptus  are missing.

:Advantage: works on large textual data, typo-insensitive
:Disadvantage: DBpedia-specific, relatively slow


_____________________________________

.. _sameas_linker:

sameas_linker
^^^^^^^^^^^^^^^
:class:`kgextension.linking.sameas_linker`

The sameAs-Linker takes URIs from a column of a dataframe and queries a
given SPARQL endpoint for resources, which are connected to these URIs via the
*owl:sameAs* predicate. Found ressources are added as new columns to the dataframe and
the dataframe is returned. It thus extracts URIs with the same meaning as the
original one.
This linker differs from the other four in that it
needs at least one URI column to be present already to generate new URIs. It can
thus be used on top of any of the other linkers.

The example shows the input dataframe to the sameas_linker: a dataframe
containing entities and their already linked URIs, in this example case from
WikiData.


+------+--------------------------------------+
| word | uri                                  |                                                            
+======+======================================+
| they | http://www.wikidata.org/entity/L1372 |  
+------+--------------------------------------+
| they | http://www.wikidata.org/entity/L493  | 
+------+--------------------------------------+
| she  | http://www.wikidata.org/entity/L1370 | 
+------+--------------------------------------+
| she  | http://www.wikidata.org/entity/L496  | 
+------+--------------------------------------+
| he   | http://www.wikidata.org/entity/L1371 | 
+------+--------------------------------------+

.. code-block:: python

    df_same_as_linked = sameas_linker(
        df, column='uri', new_attribute_name="new_link", endpoint=WikiData, 
        result_filter=None, uri_data_model=False, bundled_mode=True
    )


+------+--------------------------------------+-------------------------------------+
| word | uri                                  | new_link_1                          |                                   
+======+======================================+=====================================+
| they | http://www.wikidata.org/entity/L1372 | http://www.wikidata.org/entity/L371 |
+------+--------------------------------------+-------------------------------------+
| they | http://www.wikidata.org/entity/L493  | http://www.wikidata.org/entity/L371 | 
+------+--------------------------------------+-------------------------------------+
| she  | http://www.wikidata.org/entity/L1370 | http://www.wikidata.org/entity/L484 |
+------+--------------------------------------+-------------------------------------+
| she  | http://www.wikidata.org/entity/L496  | http://www.wikidata.org/entity/L484 |
+------+--------------------------------------+-------------------------------------+
| he   | http://www.wikidata.org/entity/L1371 | http://www.wikidata.org/entity/L485 |
+------+--------------------------------------+-------------------------------------+


Result Filtering
******************

Since the same_as linker can in some cases generate a large amount of *sameAs*
links, filtering can be applied. The result filter allows for a list of regexes
to be passed that specify URI patterns that are allowed to be returned.

.. code-block:: python

    df_same_as_linked = sameas_linker(
        df, "uri", endpoint=DBpedia, result_filter=["yago", "freebase", "wiki"]
    )

+------------------------+----------------------------------------------------+-----------------------------------------------------------+-------------------------------------+----------------------------------------+
| word                   | uri                                                | new_link_1                                                | new_link_2                          | new_link_3                             | 
+========================+====================================================+===========================================================+=====================================+========================================+
| University of Mannheim | http://dbpedia.org/resource/University_of_Mannheim | http://yago-knowledge.org/resource/University_of_Mannheim | http://rdf.freebase.com/ns/m.0b6dry | http://www.wikidata.org/entity/Q317070 |     
+------------------------+----------------------------------------------------+-----------------------------------------------------------+-------------------------------------+----------------------------------------+     
| University of Bremen   | http://dbpedia.org/resource/University_of_Bremen   | http://yago-knowledge.org/resource/University_of_Bremen   | http://rdf.freebase.com/ns/m.04fd75 | http://www.wikidata.org/entity/Q500692 |   
+------------------------+----------------------------------------------------+-----------------------------------------------------------+-------------------------------------+----------------------------------------+

The newly generated links from the sameAs-Linker follow the pattern defined by
the filter. Other links that may potentially be found are not included in the
extra URI columns but excluded because of the filter.

URI Data Model
*****************

If URI data model is chosen, the URI is directly queried instead of a SPARQL
endpoint. While this option is slower, it is more independent of the endpoint
itself. 

Bundled Mode
*************
In this default configuration, all the URIs to be queried are bundled into one
query using the Sparql VALUES method. Since this requires a Sparql 1.1
implementation this can be turned off. However, this will lead to slower
performance. 