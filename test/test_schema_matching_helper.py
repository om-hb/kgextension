import pandas as pd
import numpy as np 
import pytest
from strsimpy.levenshtein import Levenshtein

from kgextension.schema_matching_helper import calc_string_similarity, clean_string, get_common_prefixes

class TestGetCommonPrefixes():

    def test1_thres1(self):
        
        input_df = pd.read_csv("test/data/schema_matching_helper/common_prefixes.csv")
        
        output_expected = ["p1","p2","p3","pA","pB"]

        output = get_common_prefixes(input_df, threshold = 1, column_name="label")

        assert output == output_expected

    def test2_thres0(self):
        
        input_df = pd.read_csv("test/data/schema_matching_helper/common_prefixes.csv")
        
        output_expected = ["p1","p2","p3","pA","pB"]

        output = get_common_prefixes(input_df, threshold = 0, column_name="label")

        assert output == output_expected

    def test3_thres3(self):
        
        input_df = pd.read_csv("test/data/schema_matching_helper/common_prefixes.csv")
        
        output_expected = ["p1"]

        output = get_common_prefixes(input_df, threshold = 3, column_name="label")

        assert output == output_expected

    def test4_thres100(self):
        
        input_df = pd.read_csv("test/data/schema_matching_helper/common_prefixes.csv")
        
        output_expected = []

        output = get_common_prefixes(input_df, threshold = 100, column_name="label")

        assert output == output_expected


class TestCleanString():

    def test1_all_multiplecolons(self):

        common_prefixes = ["Special_Prefix_Thing"]

        string = "Special_Prefix_Thing:NameofTestElement:1"

        result_exp = "nameoftestelement1"

        result = clean_string(string, common_prefixes=common_prefixes, to_lowercase=True, remove_prefixes=True, remove_punctuation=True)

        assert result_exp == result

    def test2_all_noprefix_colon(self):

        common_prefixes = []

        string = "NameofTestElement:1"

        result_exp = "nameoftestelement1"

        result = clean_string(string, common_prefixes=common_prefixes, to_lowercase=True, remove_prefixes=True, remove_punctuation=True)

        assert result_exp == result

    def test3_lower(self):

        common_prefixes = []

        string = "NameofTestElement:1_2"

        result_exp = "nameoftestelement:1_2"

        result = clean_string(string, common_prefixes=common_prefixes, to_lowercase=True, remove_prefixes=False, remove_punctuation=False)

        assert result_exp == result

    def test4_punctuation(self):

        common_prefixes = []

        string = "NameofTestElement:1_2"

        result_exp = "NameofTestElement12"

        result = clean_string(string, common_prefixes=common_prefixes, to_lowercase=False, remove_prefixes=False, remove_punctuation=True)

        assert result_exp == result

    def test5_prefixes(self):

        common_prefixes = ["NameofTestElement", "ABC"]

        string = "NameofTestElement:1_2"

        result_exp = "1_2"

        result = clean_string(string, common_prefixes=common_prefixes, to_lowercase=False, remove_prefixes=True, remove_punctuation=False)

        assert result_exp == result

    def test6_missing(self):

        common_prefixes = ["NameofTestElement", "ABC"]

        string = np.nan

        result = clean_string(string, common_prefixes=common_prefixes, to_lowercase=True, remove_prefixes=True, remove_punctuation=True)

        assert pd.isna(result)


class TestCalcStringSimilarity:

    def test1_fullmatch(self):
    
        metrics = ["norm_levenshtein", "partial_levenshtein", "token_sort_levenshtein", "token_set_levenshtein", "ngram", "jaccard"]

        uriA = "https://test.me/A"
        uriB = "https://test.me/B"

        str_dict = {"https://test.me/A": "Hello this is a test string.", "https://test.me/B": "Hello this is a test string."}
        
        results = []

        results_exp = [1.,1.,1.,1.,1.,1.]

        for metric in metrics:

            result = calc_string_similarity(uri_1 = uriA, uri_2 = uriB, label_dict = str_dict, metric = metric )

            results.append(result)

        assert results == results_exp

    def test2_nan(self):
    
        metrics = ["norm_levenshtein", "partial_levenshtein", "token_sort_levenshtein", "token_set_levenshtein", "ngram", "jaccard"]

        uriA = "https://test.me/A"
        uriB = "https://test.me/B"

        str_dict = {"https://test.me/A": "Hello this is a test string.", "https://test.me/B": np.nan}
        
        results = []
        
        results_exp = [np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]

        for metric in metrics:

            result = calc_string_similarity(uri_1 = uriA, uri_2 = uriB, label_dict = str_dict, metric = metric )

            results.append(result)

        assert results == results_exp


    def test3_partialmatch(self):
    
        metrics = ["norm_levenshtein", "partial_levenshtein", "token_sort_levenshtein", "token_set_levenshtein", "ngram", "jaccard"]

        uriA = "https://test.me/A"
        uriB = "https://test.me/B"

        str_dict = {"https://test.me/A": "Hello this is a test string.", "https://test.me/B": "Hello this is another test string."}
        
        results = []
        
        results_exp = [0.9,0.79,0.9,0.96,1-0.19117647058823528,1-0.24137931034482762]

        for metric in metrics:

            result = calc_string_similarity(uri_1 = uriA, uri_2 = uriB, label_dict = str_dict, metric = metric )

            results.append(result)

        assert results == results_exp

    def test4_custommetric(self):
    
        metric = Levenshtein().distance

        uriA = "https://test.me/A"
        uriB = "https://test.me/B"

        str_dict = {"https://test.me/A": "Hello this is a test string.", "https://test.me/B": "Hello this is another test string."}
        
        result_exp = 6

        result = calc_string_similarity(uri_1 = uriA, uri_2 = uriB, label_dict = str_dict, metric = metric )

        assert result == result_exp

    def test5_wrongmetric(self):

        with pytest.raises(ValueError):
    
            metric = "nonexisting_metric"

            uriA = "https://test.me/A"
            uriB = "https://test.me/B"

            str_dict = {"https://test.me/A": "Hello this is a test string.", "https://test.me/B": "Hello this is a test string."}

            calc_string_similarity(uri_1 = uriA, uri_2 = uriB, label_dict = str_dict, metric = metric)
