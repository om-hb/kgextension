import numpy as np 
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from kgextension.endpoints import DBpedia
from kgextension.generator import (
    direct_type_generator, 
    data_properties_generator, 
    qualified_relation_generator, 
    unqualified_relation_generator, 
    specific_relation_generator, 
    custom_sparql_generator
)

class SpecificRelationGenerator(BaseEstimator, TransformerMixin):
    def __init__(self, columns, endpoint=DBpedia, uri_data_model=False, progress=True, 
                 direct_relation="http://purl.org/dc/terms/subject", hierarchy_relation=None, 
                 max_hierarchy_depth=1, prefix_lookup=False, caching=True):
        self.columns = columns
        self.endpoint = endpoint
        self.uri_data_model = uri_data_model
        self.progress = progress
        self.direct_relation = direct_relation
        self.hierarchy_relation = hierarchy_relation
        self.max_hierarchy_depth = max_hierarchy_depth
        self.prefix_lookup = prefix_lookup
        self.caching = caching
        
    def fit(self, X, y = None):
        return self   

    def transform(self, X, y = None):
        X = specific_relation_generator(X, self.columns, self.endpoint, self.uri_data_model, self.progress, self.direct_relation, self.hierarchy_relation, self.max_hierarchy_depth, self.prefix_lookup, caching = self.caching)
        return X 

    
class UnqualifiedRelationGenerator(BaseEstimator, TransformerMixin):
    """Unqualified relation generator creates attributes from the existence of 
    relations and adds boolean, counts, relative counts or tfidf-values features
    for incoming and outgoing relations.
    
    Args:
        BaseEstimator (sklearn.base.BaseEstimator)
        TransformerMixin (sklearn.base.TransformerMixin)
    """
    def __init__(self, columns, endpoint=DBpedia, uri_data_model=False, progress=True, prefix="Link", direction="Out", 
                 regex_filter=None, result_type="boolean", prefix_lookup=False, caching=True):
        self.columns = columns
        self.endpoint = endpoint
        self.uri_data_model = uri_data_model
        self.progress = progress
        self.prefix = prefix
        self.direction = direction
        self.regex_filter = regex_filter
        self.result_type = result_type
        self.prefix_lookup = prefix_lookup
        self.caching = caching

    def fit(self, X, y = None):
        return self   

    def transform(self, X, y = None):
        X = unqualified_relation_generator(X, self.columns, self.endpoint, self.uri_data_model, self.progress, self.prefix,                                                             self.direction, self.regex_filter, self.result_type, self.prefix_lookup, caching = self.caching)
        return X 
    

class QualifiedRelationGenerator(BaseEstimator, TransformerMixin):
    """Qualified relation generator considers not only relations, but also the 
    related types, adding boolean, counts, relative counts or tfidf-values 
    features for incoming and outgoing relations.
    
     Args:
        BaseEstimator (sklearn.base.BaseEstimator)
        TransformerMixin (sklearn.base.TransformerMixin)
    """          
    def __init__(self, columns, endpoint=DBpedia, uri_data_model=False, progress=True, prefix="Link", direction="Out", 
                 properties_regex_filter=None, types_regex_filter=None, result_type="boolean", hierarchy=False, prefix_lookup=False, caching=True):
        self.columns = columns
        self.endpoint = endpoint
        self.uri_data_model = uri_data_model
        self.progress = progress
        self.prefix = prefix
        self.direction = direction
        self.properties_regex_filter = properties_regex_filter
        self.types_regex_filter = types_regex_filter
        self.result_type = result_type
        self.hierarchy = hierarchy
        self.prefix_lookup = prefix_lookup
        self.caching = caching

    def fit(self, X, y = None):
        return self   

    def transform(self, X, y = None):
        X = qualified_relation_generator(X, self.columns, self.endpoint, self.uri_data_model, self.progress, self.prefix, 
                                         self.direction, self.properties_regex_filter, self.types_regex_filter, self.result_type, 
                                         self.hierarchy, self.prefix_lookup, caching = self.caching)
        return X


class DataPropertiesGenerator(BaseEstimator, TransformerMixin):
    def __init__(self, columns, endpoint=DBpedia, uri_data_model=False, progress=True, type_filter=None, 
                 regex_filter=None, bundled_mode=True, prefix_lookup=False, caching=True):
        self.columns = columns
        self.endpoint = endpoint
        self.uri_data_model = uri_data_model
        self.progress = progress
        self.type_filter = type_filter
        self.regex_filter = regex_filter
        self.bundled_mode = bundled_mode
        self.prefix_lookup = prefix_lookup
        self.caching = caching
     
    def fit(self, X, y = None):
        return self   

    def transform(self, X, y = None):
        X = data_properties_generator(X, self.columns, self.endpoint, self.uri_data_model, self.progress, self.type_filter,
                                      self.regex_filter, self.bundled_mode, self.prefix_lookup, caching = self.caching)
        return X 


class DirectTypeGenerator(BaseEstimator, TransformerMixin):
    def __init__(self, columns, endpoint=DBpedia, uri_data_model=False, progress=True, prefix="", regex_filter=None, 
                 result_type="boolean", bundled_mode=True, hierarchy=False, prefix_lookup=False, caching = True):
        self.columns = columns
        self.endpoint = endpoint
        self.uri_data_model = uri_data_model
        self.progress = progress
        self.prefix = prefix
        self.regex_filter = regex_filter
        self.result_type = result_type
        self.bundled_mode = bundled_mode
        self.hierarchy = hierarchy
        self.prefix_lookup = prefix_lookup
        self.caching = caching
        
    def fit(self, X, y = None):
        return self   

    def transform(self, X, y = None):
        X = direct_type_generator(X, self.columns, self.endpoint, self.uri_data_model, self.progress, self.prefix, self.regex_filter, 
                                  self.result_type, self.bundled_mode, self.hierarchy, self.prefix_lookup, caching = self.caching)
        return X 
