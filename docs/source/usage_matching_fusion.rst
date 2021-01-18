.. _matching-fusion-label:

==============================
Schema Matching & Fusion
==============================

Idea
^^^^^^^^^^^^^^^^^^^^^^

If data from different sources is used, it may be beneficial to match and fuse that data in avoid of the situation that two or more URIs represent one entity.

Basics
^^^^^^^^^^^^^^^^^^^^^^

The Schema Matching functions create a mapping of matching attributes 
in the schema based on different metrics. Multiple results of matching score from various functions can be incorporated by Combiner function into 
a single score per combination of attributes. And the final mappings can be fused by Data Fuser function with different fusion strategies, to be
selected separately for boolean, numeric and string values.

* **Types of Schema Matching Function**

  * relational_matching
  * label_schema_matching
  * string_similarity_matching
  * value_overlap_matching

* **Combiner Function**

  * matching_combiner

* **Data Fusion Functions**

  * get_fusion_clusters
  * data_fuser

Matching
^^^^^^^^^^^^^^^^^^^^^^

Relational Matching
***************************
:class:`kgextension.schema_matching.relational_matching`

The relational matching function finds that two different
resources refer to the same real-world object by querying and checking
for their sameAs links, equivalentClass links or Equivalent links. The matching information is directly obtained from Linked Open Data.
The querying predicate is ``owl:equivalentProperty|owl:equivalentClass|owl:sameAs|wdt:P1628``.

.. code-block:: python

    from kgextension.schema_matching import relational_matching

    df_relational_matcher = relational_matching(
       df, endpoints=[DBpedia, WikiData], uri_data_model=False, 
       match_score=1, progress=True, caching=True
    )

The output DataFrame of the function as example below contains combinations of every two URIs. 
If parameter *match_score* is set to 1 as default, the result value of two same URIs would be 1, otherwise would be 0.

+------------------------------------------+-----------------------------------------+-----------+
| uri_1                                    | uri_2                                   | value     |
+==========================================+=========================================+===========+
| http://dbpedia.org/ontology/Organisation | http://schema.org/Organization          |     1     |
+------------------------------------------+-----------------------------------------+-----------+
| http://dbpedia.org/ontology/country	   | http://schema.org/Organization          |     0     |
+------------------------------------------+-----------------------------------------+-----------+
| http://dbpedia.org/ontology/Organisation |http://dbpedia.org/ontology/country      |     0     |
+------------------------------------------+-----------------------------------------+-----------+

Label Schema Matching
***************************
:class:`kgextension.schema_matching.label_schema_matching`

The label schema matching function is designed to query and compare the labels of one entity
combination, and the querying predicate is ``rdfs:label``.

.. code-block:: python

    from kgextension.schema_matching import label_schema_matching

    df_label_matcher = label_schema_matching(
       df, endpoint=DBpedia, uri_data_model=False, to_lowercase=True, 
       remove_prefixes=True, remove_punctuation=True, prefix_threshold=1, 
       progress=True, caching=True
    )

The queried text field can be preprocessed before comparison in order to improve the accuracy of matching. 
The provided preprocessing methods include ``to_lowercase``: convert all letters to lowercase, 
``remove_prefixes``: remove all prefixes before label like *"Category:"*, 
and ``remove_punctuation``: remove all punctuation from the string.

The output DataFrame of the function as example below contains combinations of every two uris.
And the result value of two same labels would be 1, otherwise
would be 0. 

+------------------------------------------+-----------------------------------------+-------------+
| uri_1                                    | uri_2                                   | same_label  |
+==========================================+=========================================+=============+
| http://dbpedia.org/ontology/Organisation | http://schema.org/Organization          |     1       |
+------------------------------------------+-----------------------------------------+-------------+
| http://dbpedia.org/ontology/country	   | http://schema.org/Organization          |     0       |
+------------------------------------------+-----------------------------------------+-------------+
| http://dbpedia.org/ontology/Organisation |http://dbpedia.org/ontology/country      |     0       |
+------------------------------------------+-----------------------------------------+-------------+

String Similarity Matching
***************************
:class:`kgextension.schema_matching.string_similarity_matching`

The string similarity matching function calculates the string similarity from the text field obtained by querying the attributes for the predicate. The
calculation based on various metrics that are *Norm Levenshtein*, *Partial Levenshtein*,
*Token Sort Levenshtein*, *Token Set levenshtein*, *N-gram* and *Jaccard*.
The default querying predicate is ``rdfs:label``.

Default
"""""""""""""""""""""""""""""

.. code-block:: python

    from kgextension.schema_matching import string_similarity_matching

    df_string_similarity_matcher = string_similarity_matching(
       df, predicate="rdfs:label", to_lowercase=True, remove_prefixes=True, 
       remove_punctuation=True, similarity_metric="norm_levenshtein", 
       prefix_threshold=1, n=2, progress=True, caching=True
    )

The queried text field can be preprocessed before comparison in order to improve the accuracy of matching. 
The provided preprocessing methods include ``to_lowercase``: convert all letters to lowercase, 
``remove_prefixes``: remove all prefixes before label like *"Category:"*, 
and ``remove_punctuation``: remove all punctuation from the string.

The output DataFrame of the function with default setting would be:

+------------------------------------------+-----------------------------------------+---------------+
| uri_1                                    | uri_2                                   | value_string  |
+==========================================+=========================================+===============+
| http://dbpedia.org/ontology/Organisation |http://dbpedia.org/ontology/country      |     0.52      |
+------------------------------------------+-----------------------------------------+---------------+
| http://dbpedia.org/ontology/Organisation | http://schema.org/Organization          |     NaN       |
+------------------------------------------+-----------------------------------------+---------------+
| http://dbpedia.org/ontology/country	   | http://schema.org/Organization          |     NaN       |
+------------------------------------------+-----------------------------------------+---------------+

.. note::
    The *value_string* would be null if one or more URIs of one combination in which queried predicate is missing. For above example the *rdfs:label* of *http://schema.org/Organization* doesn't exist. 

Other Similarity Metric
""""""""""""""""""""""""""""""

parameter *n* is n-Value set for the metrics "ngram" and "jaccard". It defaults to 2.

:class:`similarity_metric="partial_levenshtein"`

+------------------------------------------+-----------------------------------------+---------------+
| uri_1                                    | uri_2                                   | value_string  |
+==========================================+=========================================+===============+
| http://dbpedia.org/ontology/Organisation |http://dbpedia.org/ontology/country      |     0.45      |
+------------------------------------------+-----------------------------------------+---------------+

:class:`similarity_metric="token_sort_levenshtein"`

+------------------------------------------+-----------------------------------------+---------------+
| uri_1                                    | uri_2                                   | value_string  |
+==========================================+=========================================+===============+
| http://dbpedia.org/ontology/Organisation |http://dbpedia.org/ontology/country      |     0.32      |
+------------------------------------------+-----------------------------------------+---------------+

:class:`similarity_metric="token_set_levenshtein"`

+------------------------------------------+-----------------------------------------+---------------+
| uri_1                                    | uri_2                                   | value_string  |
+==========================================+=========================================+===============+
| http://dbpedia.org/ontology/Organisation |http://dbpedia.org/ontology/country      |     0.32      |
+------------------------------------------+-----------------------------------------+---------------+

:class:`similarity_metric="ngram"`

+------------------------------------------+-----------------------------------------+---------------+
| uri_1                                    | uri_2                                   | value_string  |
+==========================================+=========================================+===============+
| http://dbpedia.org/ontology/Organisation |http://dbpedia.org/ontology/country      |     1.0       |
+------------------------------------------+-----------------------------------------+---------------+

:class:`similarity_metric="jaccard"`

+------------------------------------------+-----------------------------------------+---------------+
| uri_1                                    | uri_2                                   | value_string  |
+==========================================+=========================================+===============+
| http://dbpedia.org/ontology/Organisation |http://dbpedia.org/ontology/country      |     0.0       |
+------------------------------------------+-----------------------------------------+---------------+

Value Overlap Matching
***************************
:class:`kgextension.schema_matching.value_overlap_matching`

The value overlap matching function calculates the ratio of overlapping values
of two columns of a DataFrame with row-wise comparison. The value overlap
is calculated by dividing equivalence by the total number of entity values.

.. code-block:: python

    from kgextension.schema_matching import value_overlap_matching

    df_value_matcher = value_overlap_matching(
       df, progress=True
    )

+------------------------------------------+-----------------------------------------+----------------+
| uri_1                                    | uri_2                                   | value_overlap  |
+==========================================+=========================================+================+
| http://dbpedia.org/ontology/Organisation |http://dbpedia.org/ontology/country      |     0.75       |
+------------------------------------------+-----------------------------------------+----------------+
| http://dbpedia.org/ontology/country	   | http://schema.org/Organization          |     0.75       |
+------------------------------------------+-----------------------------------------+----------------+
|http://dbpedia.org/ontology/Organisation  | http://schema.org/Organization          |     1.00       |
+------------------------------------------+-----------------------------------------+----------------+

Combine Matchings
^^^^^^^^^^^^^^^^^^^^^^

Matching Combiner
***************************
:class:`kgextension.schema_matching.matching_combiner`

It combines results of the schema matching functions
into a single similarity score per combination of attributes. There are 5
methods for combining the individual scores: *Maximum*, *Minimum*, *Average*,
*Weighted* and *Thresholding*.

Here we use the result DataFrame of above schema matching functions with default setting as input.

Default: Method-*Average*
""""""""""""""""""""""""""""

.. code-block:: python

    from kgextension.schema_matching import matching_combiner

    df_combiner = matching_combiner(
       matching_result_dfs=[df_relational_matcher, df_label_matcher,
        df_string_similarity_matcher, df_value_matcher], 
       method="avg", columns=None, 
       ignore_single_missings=False, weights=None, 
       thresholds=None, merge_on=["uri_1", "uri_2"]
    )

This method calculates the mean value of all input matching result DataFrame as column *"result"*.
The output DataFrame would be like below, similar as the result of schema matching functions.

+------------------------------------------+-----------------------------------------+----------------+
| uri_1                                    | uri_2                                   | result         |
+==========================================+=========================================+================+
| http://dbpedia.org/ontology/Organisation |http://dbpedia.org/ontology/country      |     0.423333   |
+------------------------------------------+-----------------------------------------+----------------+
| http://dbpedia.org/ontology/country	   | http://schema.org/Organization          |     0.375000   |
+------------------------------------------+-----------------------------------------+----------------+
|http://dbpedia.org/ontology/Organisation  | http://schema.org/Organization          |     1.000000   |
+------------------------------------------+-----------------------------------------+----------------+

Other Methods
"""""""""""""""""""""

:class:`method="max"`

This method calculates the maximum value of all input matching result DataFrame as column *"result"*.

+------------------------------------------+-----------------------------------------+----------------+
| uri_1                                    | uri_2                                   | result         |
+==========================================+=========================================+================+
| http://dbpedia.org/ontology/Organisation |http://dbpedia.org/ontology/country      |     0.75       |
+------------------------------------------+-----------------------------------------+----------------+
| http://dbpedia.org/ontology/country	   | http://schema.org/Organization          |     0.75       |
+------------------------------------------+-----------------------------------------+----------------+
|http://dbpedia.org/ontology/Organisation  | http://schema.org/Organization          |     1.00       |
+------------------------------------------+-----------------------------------------+----------------+

:class:`method="min"`

This method calculates the minimum value of all input matching result DataFrame as column *"result"*.

+------------------------------------------+-----------------------------------------+----------------+
| uri_1                                    | uri_2                                   | result         |
+==========================================+=========================================+================+
| http://dbpedia.org/ontology/Organisation |http://dbpedia.org/ontology/country      |     0          |
+------------------------------------------+-----------------------------------------+----------------+
| http://dbpedia.org/ontology/country	   | http://schema.org/Organization          |     0          |
+------------------------------------------+-----------------------------------------+----------------+
|http://dbpedia.org/ontology/Organisation  | http://schema.org/Organization          |     1          |
+------------------------------------------+-----------------------------------------+----------------+

For using *Weighted* and *Thresholding* two metrics,
users need to input their subjective weight or threshold for every values
of one entity. 

:class:`method="weighted", weight=[0.2,0.2,0.4,0.2]`

The result of this method would be the sum of each value of input matching result DataFrame multiple customized weight.

+------------------------------------------+-----------------------------------------+----------------+
| uri_1                                    | uri_2                                   | result         |
+==========================================+=========================================+================+
| http://dbpedia.org/ontology/Organisation |http://dbpedia.org/ontology/country      |     0.358000   |
+------------------------------------------+-----------------------------------------+----------------+
| http://dbpedia.org/ontology/country	   | http://schema.org/Organization          |     NaN        |
+------------------------------------------+-----------------------------------------+----------------+
|http://dbpedia.org/ontology/Organisation  | http://schema.org/Organization          |     NaN        |
+------------------------------------------+-----------------------------------------+----------------+

:class:`method="thresholding", thresholds=[0.7,0.7,0.7,0.7]`

The result of this method would be the sum of times that each value of input matching result DataFrame is higher or equal to the customized threshold.

+------------------------------------------+-----------------------------------------+----------------+
| uri_1                                    | uri_2                                   | result         |
+==========================================+=========================================+================+
| http://dbpedia.org/ontology/Organisation |http://dbpedia.org/ontology/country      |     1          |
+------------------------------------------+-----------------------------------------+----------------+
| http://dbpedia.org/ontology/country	   | http://schema.org/Organization          |     NaN        |
+------------------------------------------+-----------------------------------------+----------------+
|http://dbpedia.org/ontology/Organisation  | http://schema.org/Organization          |     NaN        |
+------------------------------------------+-----------------------------------------+----------------+

Users can also turn to *ignore single missing* and then no null
similarity value would appear in the final result.

:class:`method="thresholding", thresholds=[0.7,0.7,0.7,0.7], ignore_single_missings=True`

Then the result DataFrame would be:

+------------------------------------------+-----------------------------------------+----------------+
| uri_1                                    | uri_2                                   | result         |
+==========================================+=========================================+================+
| http://dbpedia.org/ontology/Organisation |http://dbpedia.org/ontology/country      |     1          |
+------------------------------------------+-----------------------------------------+----------------+
| http://dbpedia.org/ontology/country	   | http://schema.org/Organization          |     1          |
+------------------------------------------+-----------------------------------------+----------------+
|http://dbpedia.org/ontology/Organisation  | http://schema.org/Organization          |     3          |
+------------------------------------------+-----------------------------------------+----------------+


Fusion
^^^^^^^^^^^^^^^^^^^^^^

Get Fusion Clusters
***************************
:class:`kgextension.fusion.get_fusion_clusters`

The get fusion clusters function for creating clusters with the
matching column names as sets according to the threshold set by users, and the input
DataFrame should be the result of function Matching Combiner. For example, the 
pairs {car, auto} and {car, automobile} would be clustered into the set 
{car, auto, automobile} (if both pairs have a similarity ≥ the specified threshold).

.. code-block:: python

    from kgextension.fusion import get_fusion_clusters

    clusters = get_fusion_clusters(
       df_combiner, threshold=0.85, progress=True
    )

In our example, the function returns:

.. code-block:: python

    [{'http://dbpedia.org/ontology/Organisation',
      'http://schema.org/Organization'}]
    


Data Fuser
***************************
:class:`kgextension.fusion.data_fuser`

The data fuser function can fuse the columns in the matching sets of the clusters.
The available fuser metrics can be selected separately for boolean, numeric and
string values as shown in below Table. Other existing and user-defined functions
can also be passed as well when they are applicable to pd.DataFrame.apply(axis=1).
The final output would be a DataFrame that contains no more than one URI for each entity.

.. code-block:: python

    from kgextension.fusion import get_fusion_clusters

    df_fused = data_fuser(
       df, clusters, boolean_method_single="provenance", 
       boolean_method_multiple="voting", numeric_method_single="average", 
       numeric_method_multiple="average", string_method_single="longest",
       string_method_multiple="longest", provenance_regex="http://dbpedia.org/",
       progress=True
    )

Fuser Metrics for Different Type and Size Matchers
"""""""""""""""""""""""""""""""""""""""""""""""""""""

The following table list for specific data type and matchers size, which kind of fuser metrics are available.

+------------------------------+--------------+---------------+---------------+
| Data Type                    | Boolean      | Numeric       | String        |
+==============================+==============+===============+===============+
| Fuser Metrics                | - First      | - Minimum     | - First       |
|                              | - last       | - Maximum     | - last        |
|                              | - Random     | - Average     | - Longest     |
|                              | - Provenance | - Random      | - Shortest    |
|                              |              | - Provenance  | - Random      |
|                              |              |               | - Provenance  |
+------------------------------+--------------+---------------+---------------+
| Only for Multiple Matchers   | Voting       | - Voting      | Voting        |
|                              |              | - Median      |               |
+------------------------------+--------------+---------------+---------------+

.. note::
    The metrics *Voting* and *Median* have been asserted in the function that they cannot
    be applied in single matches (a pair).
