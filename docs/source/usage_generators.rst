====================
Generators
====================

- data_properties_generator_.
- direct_type_generator_.
- unqualified_relation_generator_.
- qualified_relation_generator_.
- specific_relation_generator_.
- custom_sparql_generator_.

Overview
^^^^^^^^

The generators extract data from a knowledge graph in different ways.
The newly generated features are added to the pandas DataFrame in form of additional columns. 
To connect to a knowledge graph, the input DataFrame should contain at least
one column holding URIs. 

Apart from the feature generation, most generators also have the option to create a hierarchy of
the features generated, which can be used for later filtering with one of the
:ref:`feature-selection-label` functions.

Some of the generators support different result types:

- **Boolean**: True if a certain caracteristic is
  fulfilled and false if not
- **Counts**: Count the occurences of a certain characteristic
- **Relative counts**: Count the occurences of a certain characteristic in
  relation to the total number of occurences
- **TF-IDF**: Similar feature as relative counts, but weighs the percentage
  with the overall occurrence of a characteristic in the dataset 

The input to the generators is a :class:`pandas.DataFrame` with
at least one column containing URIs linking the entities to a knowledge graph.
Usually this columns is added to the DataFrame by a :ref:`linker-label` function.

+-----------+-----------------------------------+
| country   | link                              |
+===========+===================================+
| Spain     | http://dbpedia.org/resource/Spain |
+-----------+-----------------------------------+
| Japan     | http://dbpedia.org/resource/Japan |
+-----------+-----------------------------------+
| Chile     | http://dbpedia.org/resource/Chile |
+-----------+-----------------------------------+

.. _data_properties_generator:

Data Properties Generator
^^^^^^^^^^^^^^^^^^^^^^^^^
:class:`kgextension.generator.data_properties_generator`

The data properties generator creates an attribute for each literal value that
the linked entity has. The following example uses the default parameter settings:

.. code-block:: python
    
    from kgextension.generator import data_properties_generator

    df_data_properties = data_properties_generator(df_linked, "link")

+-----------+-----------------------------------+------------------------------------------------------+---------------------------------------------------------------+
| country   | link                              |   link_data_http://dbpedia.org/ontology/currencyCode |   link_data_http://dbpedia.org/ontology/humanDevelopmentIndex |
+===========+===================================+======================================================+===============================================================+
| Spain     | http://dbpedia.org/resource/Spain |                                                  EUR |                                                        0.893  |
+-----------+-----------------------------------+------------------------------------------------------+---------------------------------------------------------------+
| Japan     | http://dbpedia.org/resource/Japan |                                                  JPY |                                                        0.915  |
+-----------+-----------------------------------+------------------------------------------------------+---------------------------------------------------------------+
| Chile     | http://dbpedia.org/resource/Chile |                                                  CLP |                                                        0.847  |
+-----------+-----------------------------------+------------------------------------------------------+---------------------------------------------------------------+

The column header of a new attribute shows the origin of its values. In
the example *link_data_http://dbpedia.org/ontology/currencyCode* from the
results, the prefix *link* indicates that the data was queried from the URIs in the column
*link*, the prefix *data* stands for the generator function that was used and *http://dbpedia.org/ontology/currencyCode* is the URI of the
respective property.

Following example shows the rdf-triple, from which the
generator creates the attribute *currencyCode* with the value "EUR" for "Spain":

<http://dbpedia.org/resource/Spain> <http://dbpedia.org/ontology/currencyCode> "EUR"

Type Filter
***********

The data properties generator usually returns a large number of new attributes
of different types. With the type filter it is possible to limit the results to
certain datatypes or to explicitly exclude a datatype from the results.

In this example, only properties of the datatype *xsd:double* are added:

.. code-block:: python
    
    from kgextension.generator import data_properties_generator

    df_data_properties = data_properties_generator(
        df_linked, "link",
        type_filter="xsd:double"
        )

A datatype can be excluded by prepending a "- ":

.. code-block:: python
    
    from kgextension.generator import data_properties_generator

    df_data_properties = data_properties_generator(
        df_linked, "link",
        type_filter="- xsd:string"
        )


.. _direct_type_generator:

Direct Type Generator
^^^^^^^^^^^^^^^^^^^^^
:class:`kgextension.generator.direct_type_generator`

The direct type generator extracts the type(s) of the linked ressources (using
*rdf:type*). The resulting types are added as new columns, which are filled
either with a boolean indicator or a count. The following example uses the default parameter settings:

.. code-block:: python
    
    from kgextension.generator import direct_type_generator

    df_direct_type = direct_type_generator(df_linked, "link")

+-----------+-----------------------------------+-----------------------------------------------------+--------------------------------------------------------------------------+
| country   | link                              |   	link_type_http://dbpedia.org/ontology/Country |   link_type_http://dbpedia.org/class/yago/WikicatCountriesInSouthAmerica |
+===========+===================================+=====================================================+==========================================================================+
| Spain     | http://dbpedia.org/resource/Spain |                                                True |                                                             False        |
+-----------+-----------------------------------+-----------------------------------------------------+--------------------------------------------------------------------------+
| Japan     | http://dbpedia.org/resource/Japan |                                                True |                                                               False      |
+-----------+-----------------------------------+-----------------------------------------------------+--------------------------------------------------------------------------+
| Chile     | http://dbpedia.org/resource/Chile |                                                True |                                                                True      |
+-----------+-----------------------------------+-----------------------------------------------------+--------------------------------------------------------------------------+

Following example shows the rdf-triple, from which the
generator creates the attribute *WikicatCountriesInSouthAmerica* being 
True for "Chile":

<http://dbpedia.org/resource/Chile> rdf:Type <http://dbpedia.org/class/yago/WikicatCountriesInSouthAmerica>

.. _unqualified_relation_generator:

Unqualified Relation Generator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:class:`kgextension.generator.unqualified_relation_generator`

The unqualified relation generator creates attributes from the existence of
relations. The following example uses the default parameter settings:

.. code-block:: python
    
    from kgextension.generator import unqualified_relation_generator

    df_unqualified_relation = unqualified_relation_generator(df_linked, "link")

+-----------+-----------------------------------+-----------------------------------------------------+--------------------------------------------------------------------------+
| country   | link                              |Link_Out_boolean_http://dbpedia.org/ontology/capital |                  Link_Out_boolean_http://dbpedia.org/property/nativeName |
+===========+===================================+=====================================================+==========================================================================+
| Spain     | http://dbpedia.org/resource/Spain |                                                True |                                                                    False |
+-----------+-----------------------------------+-----------------------------------------------------+--------------------------------------------------------------------------+
| Japan     | http://dbpedia.org/resource/Japan |                                                True |                                                                     True |
+-----------+-----------------------------------+-----------------------------------------------------+--------------------------------------------------------------------------+
| Chile     | http://dbpedia.org/resource/Chile |                                                True |                                                                    False |
+-----------+-----------------------------------+-----------------------------------------------------+--------------------------------------------------------------------------+

Following example shows the rdf-triples, from which the
generator creates the attribute *Capital* being True for "Japan":

<http://dbpedia.org/resource/Japan> <http://dbpedia.org/ontology/Capital> <http://dbpedia.org/resource/Tokyo>

The value is set to True, because the relation
<http://dbpedia.org/ontology/Capital> exists for <http://dbpedia.org/resource/Japan>.


.. _qualified_relation_generator:

Qualified Relation Generator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:class:`kgextension.generator.qualified_relation_generator`

The qualified relation generator creates attributes from the existence of
relations and takes also the types of the related resources into account.
The following example uses the default parameter settings:

.. code-block:: python
    
    from kgextension.generator import qualified_relation_generator

    df_qualified_relation = qualified_relation_generator(df_linked, "link")

+-----------+-----------------------------------+------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| country   | link                              | Link_Out_boolean_http://dbpedia.org/ontology/currency_type_http://dbpedia.org/class/yago/WikicatCurrenciesOfAsia | Link_Out_boolean_http://dbpedia.org/ontology/capital_type_http://dbpedia.org/class/yago/WikicatCapitalsInEurope |
+===========+===================================+==================================================================================================================+=================================================================================================================+
| Spain     | http://dbpedia.org/resource/Spain |                                                                                                            False |                                                                                                            True |
+-----------+-----------------------------------+------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| Japan     | http://dbpedia.org/resource/Japan |                                                                                                             True |                                                                                                           False |
+-----------+-----------------------------------+------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+
| Chile     | http://dbpedia.org/resource/Chile |                                                                                                            False |                                                                                                           False |
+-----------+-----------------------------------+------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------+

Following example shows the rdf-triples, from which the
generator creates the attribute *Capital_type_WikicatCapitalsInEurope* being True for "Spain":

<http://dbpedia.org/resource/Spain> <http://dbpedia.org/ontology/Capital> <http://dbpedia.org/resource/Madrid> 

<http://dbpedia.org/resource/Madrid> rdf:type <http://dbpedia.org/class/yago/WikicatCapitalsInEurope>

The value is set to True, because <http://dbpedia.org/resource/Madrid> is the <http://dbpedia.org/ontology/Capital> of
"Spain" and is of type <http://dbpedia.org/class/yago/WikicatCapitalsInEurope>.

.. _specific_relation_generator:

Specific Relation Generator
^^^^^^^^^^^^^^^^^^^^^^^^^^^
:class:`kgextension.generator.specific_relation_generator`

The specific relation generator creates attributes from a specific direct
relation (default = "http://purl.org/dc/terms/subject"). The following example uses the default parameter settings:

.. code-block:: python
    
    from kgextension.generator import specific_relation_generator

    df_specific_relation = specific_relation_generator(df_linked, "link")

+-----------+-----------------------------------+------------------------------------------------------------------------------+---------------------------------------------------------------------------+
| country   | link                              | link_in_boolean_http://dbpedia.org/resource/Category:Former_Spanish_colonies | link_in_boolean_http://dbpedia.org/resource/Category:East_Asian_countries |
+===========+===================================+==============================================================================+===========================================================================+
| Spain     | http://dbpedia.org/resource/Spain |                                                                        False |                                                                     False |
+-----------+-----------------------------------+------------------------------------------------------------------------------+---------------------------------------------------------------------------+
| Japan     | http://dbpedia.org/resource/Japan |                                                                        False |                                                                      True |
+-----------+-----------------------------------+------------------------------------------------------------------------------+---------------------------------------------------------------------------+
| Chile     | http://dbpedia.org/resource/Chile |                                                                         True |                                                                     False |
+-----------+-----------------------------------+------------------------------------------------------------------------------+---------------------------------------------------------------------------+

Following example shows the rdf-triple, from which the
generator creates the attribute *Category:Former_Spanish_colonies* being 
True for "Chile":

<http://dbpedia.org/resource/Chile> <http://purl.org/dc/terms/subject> <http://dbpedia.org/resource/Category:East_Asian_countries>


Hierarchy Relation
******************

With the specific relation generator it is also possible to create a hierarchy
of the attributes with a user-defined hierarchy relation. The resulting
hierarchy is appended to the DataFrame.

.. code-block:: python
    
    from kgextension.generator import specific_relation_generator

    df_specific_relation = specific_relation_generator(
        df_linked, "link",
        hierarchy_relation="http://www.w3.org/2004/02/skos/core#broader"
        )

.. _custom_sparql_generator:

Custom SPARQL Generator
^^^^^^^^^^^^^^^^^^^^^^^
:class:`kgextension.generator.custom_sparql_generator`

The custom SPARQL generator allows you to define your own SPARQL query and
creates additional attributes from the query results. Within the SPARQL query
you can use links generated by linkers as placeholders, enclosed in asterisks.
In the following example the Gini coefficient of the countries in the
DataFrame is queried. When the query is executed, the placeholder \*link\* in
the query is replaced by the value in the column *link* of the respective entity.

.. code-block:: python
    
    from kgextension.generator import custom_sparql_generator

    query = "select ?gini where {*link* <http://dbpedia.org/ontology/giniCoefficient> ?gini}"

    df_custom_sparql = custom_sparql_generator(df_linked, "link", query)

+-----------+-----------------------------------+------+
| country   | link                              | gini |
+===========+===================================+======+
| Spain     | http://dbpedia.org/resource/Spain | 33.0 |
+-----------+-----------------------------------+------+
| Japan     | http://dbpedia.org/resource/Japan | 33.9 |
+-----------+-----------------------------------+------+
| Chile     | http://dbpedia.org/resource/Chile | 44.4 |
+-----------+-----------------------------------+------+