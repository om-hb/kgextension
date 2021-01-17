import numpy as np 
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from kgextension.fusion import get_fusion_clusters, data_fuser
from kgextension.schema_matching import matching_combiner

class MatchingFuser(BaseEstimator, TransformerMixin):
    def __init__(self, matching_functions, threshold=0.85, method="avg", columns=None, ignore_single_missings=False, 
                 weights=None, merge_on=["uri_1", "uri_2"], boolean_method_single="provenance", 
                 boolean_method_multiple="voting", numeric_method_single="average", numeric_method_multiple="average", 
                 string_method_single="longest", string_method_multiple="longest", provenance_regex="http://dbpedia.org/", 
                 progress=True,
                 caching=True):
        self.matching_functions = matching_functions
        self.threshold = threshold
        self.method = method
        self.columns = columns
        self.ignore_single_missings = ignore_single_missings
        self.weights = weights
        self.merge_on = merge_on
        self.boolean_method_single = boolean_method_single
        self.boolean_method_multiple = boolean_method_multiple
        self.numeric_method_single = numeric_method_single
        self.numeric_method_multiple = numeric_method_multiple
        self.string_method_single = string_method_single
        self.string_method_multiple = string_method_multiple
        self.provenance_regex = provenance_regex
        self.progress = progress
        self.caching = caching
        
    def fit(self, X, y = None):
        return self   

    def transform(self, X, y = None):
        #TODO: Add progress & caching attribute to matching_function call?
        result_dfs = [func(X) for func in self.matching_functions]
        combined = matching_combiner(
            matching_result_dfs=result_dfs, method=self.method, columns=self.columns, 
            ignore_single_missings=self.ignore_single_missings, weights=self.weights, 
            merge_on=self.merge_on
        )
        clusters = get_fusion_clusters(combined, self.threshold, progress=self.progress)
        X = data_fuser(
            X, clusters, self.boolean_method_single, self.boolean_method_multiple, self.numeric_method_single, 
            self.numeric_method_multiple, self.string_method_single, self.string_method_multiple, self.provenance_regex, progress=self.progress
        )   
        return X 

