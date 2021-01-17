import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from kgextension.endpoints import DBpedia
from kgextension.linking import pattern_linker, dbpedia_spotlight_linker, dbpedia_lookup_linker, label_linker, sameas_linker


class PatternLinker(BaseEstimator, TransformerMixin):
    def __init__(self, column, new_attribute_name="new_link", progress=True, base_url="www.dbpedia.org/resource/",
                 url_encoding=True, DBpedia_link_format=True):
        self.column = column
        self.new_attribute_name = new_attribute_name
        self.progress = progress
        self.base_url = base_url
        self.url_encoding = url_encoding
        self.DBpedia_link_format = DBpedia_link_format

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X = pattern_linker(X, column=self.column, new_attribute_name=self.new_attribute_name, progress=self.progress,
                           base_url=self.base_url, url_encoding=self.url_encoding,
                           DBpedia_link_format=self.DBpedia_link_format)
        return X


class DbpediaSpotlightLinker(BaseEstimator, TransformerMixin):
    def __init__(self, column, new_attribute_name="new_link", progress=True, max_hits=1, language="en",
                 selection='first', confidence=0.3, support=5, min_similarity_score=0.5, caching=True):

        self.column = column
        self.new_attribute_name = new_attribute_name
        self.progress = progress
        self.max_hits = max_hits
        self.language = language
        self.selection = selection
        self.confidence = confidence
        self.support = support
        self.min_similarity_score = min_similarity_score
        self.caching = caching

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X = dbpedia_spotlight_linker(X, column=self.column, new_attribute_name=self.new_attribute_name,
                                     progress=self.progress, max_hits=self.max_hits, language=self.language,
                                     selection=self.selection, confidence=self.confidence, support=self.support,
                                     min_similarity_score=self.min_similarity_score, caching = self.caching)
        return X


class DbpediaLookupLinker(BaseEstimator, TransformerMixin):
    def __init__(self, column, new_attribute_name="new_link", progress=True,
                 base_url="http://lookup.dbpedia.org/api/search/", max_hits=1, query_class="",
                 lookup_api="KeywordSearch", caching=True):

        self.column = column
        self.new_attribute_name = new_attribute_name
        self.progress = progress
        self.base_url = base_url
        self.max_hits = max_hits
        self.query_class = query_class
        self.lookup_api = lookup_api
        self.caching = caching

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X = dbpedia_lookup_linker(
            X, column=self.column, new_attribute_name=self.new_attribute_name, progress=self.progress,
            max_hits=self.max_hits, query_class=self.query_class, lookup_api=self.lookup_api, caching = self.caching)
        return X


class LabelLinker(BaseEstimator, TransformerMixin):
    def __init__(self, column, new_attribute_name="new_link", progress=True, endpoint=DBpedia,
                 result_filter=None, language="en", max_hits=1, label_property="rdfs:label", prefix_lookup=False, caching=True):

        self.column = column
        self.new_attribute_name = new_attribute_name
        self.progress = progress
        self.endpoint = endpoint
        self.result_filter = result_filter
        self.language = language
        self.max_hits = max_hits
        self.label_property = label_property
        self.prefix_lookup = prefix_lookup
        self.caching = caching

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X = label_linker(X, column=self.column, new_attribute_name=self.new_attribute_name,
                         progress=self.progress, endpoint=self.endpoint, result_filter=self.result_filter,
                         language=self.language, max_hits=self.max_hits, label_property=self.label_property, prefix_lookup=self.prefix_lookup, caching = self.caching)
        return X


class SameAsLinker(BaseEstimator, TransformerMixin):
    def __init__(self, column, new_attribute_name="new_link", progress=True, endpoint=DBpedia,
                 result_filter=None, uri_data_model=False, prefix="", bundled_mode=True, prefix_lookup=False, caching=True):

        self.column = column
        self.new_attribute_name = new_attribute_name
        self.progress = progress
        self.endpoint = endpoint
        self.result_filter = result_filter
        self.uri_data_model = uri_data_model
        self.prefix = prefix
        self.bundled_mode = bundled_mode
        self.prefix_lookup = prefix_lookup
        self.caching = caching

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X = sameas_linker(X, column=self.column, new_attribute_name=self.new_attribute_name,
                          progress=self.progress, endpoint=self.endpoint, result_filter=self.result_filter,
                          uri_data_model=self.uri_data_model, bundled_mode=self.bundled_mode, 
                          prefix_lookup=self.prefix_lookup, caching = self.caching)
        return X
