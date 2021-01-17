from sklearn.base import BaseEstimator, TransformerMixin

from kgextension.endpoints import DBpedia
from kgextension.utilities import check_uri_redirects


class CheckUriRedirects(BaseEstimator, TransformerMixin):
    def __init__(self, column, replace=True, custom_name_postfix=None,
                 redirection_property="http://dbpedia.org/ontology/wikiPageRedirects",
                 endpoint=DBpedia, regex_filter="dbpedia", bundled_mode=True, uri_data_model=False,
                 progress=True, caching=True):

        self.column = column
        self.replace = replace
        self.custom_name_postfix = custom_name_postfix
        self.redirection_property = redirection_property
        self.endpoint = endpoint
        self.regex_filter = regex_filter
        self.bundled_mode = bundled_mode
        self.uri_data_model = uri_data_model
        self.progress = progress
        self.caching = caching

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X = check_uri_redirects(X, column=self.column, replace=self.replace, custom_name_postfix=self.custom_name_postfix,
                                redirection_property=self.redirection_property, endpoint=self.endpoint, regex_filter=self.regex_filter,
                                bundled_mode=self.bundled_mode, uri_data_model=self.uri_data_model, progress=self.progress, caching = self.caching)
        return X
