import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from kgextension.endpoints import DBpedia
from kgextension.feature_selection import (greedy_top_down_filter,
                                           hierarchy_based_filter,
                                           hill_climbing_filter,
                                           tree_based_filter)


class HillClimbingFilter(BaseEstimator, TransformerMixin):
    """Feature selection performed by comparing nodes with their parents in a
       bottom-up approach.

       Wang, B.B., Mckay, R.B., Abbass, H.A. and Barlow, M., 2003, February. A
       comparative study for domain ontology guided feature extraction. In
       Proceedings of the 26th Australasian computer science conference-Volume
       16 (pp. 69-78).
       Can be used in a sklearn pipeline.

    Args:
        BaseEstimator (sklearn.base.BaseEstimator)
        TransformerMixin (sklearn.base.TransformerMixin)
    """
    def __init__(self, label_column, metric='hill_climbing_cost_function', G=None, beta=0.05, k=5, progress=True, **kwargs):
        self.label_column = label_column
        self.metric = metric
        self.G = G
        self.beta = beta
        self.k = k
        self.progress = progress

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X = hill_climbing_filter(X, self.label_column, self.metric,
                                 self.G, self.beta, self.k, self.progress)
        return X


class HierarchyBasedFilter(BaseEstimator, TransformerMixin):
    """Feature selection approach, namely, SHSEL including the initial selection 
    algorithm and pruning algorithm. Identify and filter out the ranges of nodes 
    with similar relevance in each branch of the hierarchy. 
    It can be used in a sklearn pipeline. 
    
    Ristoski, P. and Paulheim, H., 2014, October. Feature selection in 
    hierarchical feature spaces. In International conference on discovery 
    science (pp. 288-300). Springer, Cham.
    
    Args:
        BaseEstimator (sklearn.base.BaseEstimator)
        TransformerMixin (sklearn.base.TransformerMixin)
    """
    def __init__(self, label_column, G=None, threshold=0.99, metric="info_gain", 
                 pruning=True, all_remove=True, progress=True,  **kwargs):
        self.label_column = label_column
        self.G = G
        self.threshold = threshold
        self.metric = metric
        self.pruning = pruning
        self.all_remove = all_remove
        self.progress = progress

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X = hierarchy_based_filter(X, self.label_column, self.G, self.threshold,
                                   self.metric, self.pruning, 
                                   self.all_remove, self.progress)
        return X


class GreedyTopDownFilter(BaseEstimator, TransformerMixin):
    def __init__(self, label_column, column_prefix = "new_link_type_", G=None, progress=True):
        self.label_column = label_column
        self.column_prefix = column_prefix
        self.G = G
        self.progress = progress

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X = greedy_top_down_filter(
            X, self.label_column, self.column_prefix, self.G, self.progress)
        return X


class TreeBasedFilter(BaseEstimator, TransformerMixin):
    def __init__(self, label_column, G=None, metric="Lift", progress=True):
        self.label_column = label_column
        self.G = G
        self.metric = metric
        self.progress = progress

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X = tree_based_filter(X, self.label_column,
                              self.G, self.metric, self.progress)
        return X
