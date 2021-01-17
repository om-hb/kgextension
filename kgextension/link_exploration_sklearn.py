import numpy as np 
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from kgextension.endpoints import DBpedia
from kgextension.link_exploration import link_explorer

class LinkExplorer(BaseEstimator, TransformerMixin):
    def __init__(self, links, number_of_hops = 1, link_to_follow = "owl:sameAs", progress=True, caching=True):
        self.links = links
        self.number_of_hops = number_of_hops
        self.link_to_follow = link_to_follow
        self.progress = progress
        self.caching = caching
     
        #TODO: Doesn't seem up to date!

    def fit(self, X, y = None):
        return self   

    def transform(self, X, y = None):
        X = link_explorer(X, self.links, self.number_of_hops, self.link_to_follow, progress=self.progress, caching=self.caching)
        return X