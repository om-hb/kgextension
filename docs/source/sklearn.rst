====================================
Scikit-Learn Pipeline Integration
====================================

The feature generation process of this package follows a certain workflow;
first, the connection to the knowledge graph entities is established (see
:ref:`linker-label`), then features are generated (see :ref:`generator-label`).
Optionally, more links can be obtained by using the
:ref:`link-exploration-label`. For the subsequent filtering of the additional
features, the :ref:`feature-selection-label` algorithms can be used. In case of
URI features referring to the same entity, :ref:`matching-fusion-label` can be
applied.

For convenience, this workflow can be applied within a scikit-learn pipeline.
The following example shows how to set up the pipeline in order to generate and
filter features for this example dataframe:

+-------------------+------------+
| author            | book_sales |
+===================+============+
| Stephen King      | 20         |
+-------------------+------------+
| Joanne K. Rowling | 25         |
+-------------------+------------+
| Dan Brown         | 18         |
+-------------------+------------+

.. code-block:: python

    import pandas as pd
    from sklearn.pipeline import Pipeline 

    from kgextension.linking_sklearn import DbpediaLookupLinker
    from kgextension.generator_sklearn import SpecificRelationGenerator, DirectTypeGenerator
    from kgextension.feature_selection_sklearn import HierarchyBasedFilter

    # input DataFrame
    df = pd.DataFrame({
        'author': ['Stephen King', 'Joanne K. Rowling', 'Dan Brown'],
        'book_sales': [20, 25, 18]
    })

    # set up the parts of the pipeline
    Linker = DbpediaLookupLinker(column='author')
    Generator1 = SpecificRelationGenerator(columns=['new_link'])
    Generator2 = DirectTypeGenerator(columns=['new_link'], hierarchy=True)
    Filter = HierarchyBasedFilter(label_column='book_sales')

    # combine the functions into the pipeline
    pipeline = Pipeline(steps = [('lookup_linker', Linker),
                                 ('sr_generator', Generator1),
                                 ('dt_generator', Generator2),
                                 ('hb_filter', Filter)])

    # fit and transform the input data
    pipeline.fit_transform(df)


