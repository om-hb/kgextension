import pandas as pd
import numpy as np 
import pytest


from kgextension.endpoints import DBpedia
from kgextension.schema_matching import (
    relational_matching, 
    label_schema_matching, 
    value_overlap_matching, 
    string_similarity_matching
)


class TestRelationalMatching:

    def test1_default(self):
        path_input = "test/data/schema_matching/default_matches_cities_input.csv"
        df = pd.read_csv(path_input)

        path_expected = "test/data/schema_matching/default_matches_cities_expected.csv"
        expected_matches = pd.read_csv(path_expected)

        output_matches = relational_matching(df)
        output_matches['value'] = pd.to_numeric(output_matches['value'])

        pd.testing.assert_frame_equal(
            output_matches, expected_matches, check_like=True)

    def test2_no_matches(self):
        path_input = "test/data/schema_matching/no_matches_cities_input.csv"
        df = pd.read_csv(path_input)

        path_expected = "test/data/schema_matching/no_matches_cities_expected.csv"
        expected_matches = pd.read_csv(path_expected)

        output_matches = relational_matching(df)
        output_matches['value'] = pd.to_numeric(output_matches['value'])

        pd.testing.assert_frame_equal(
            output_matches, expected_matches, check_like=True)

    def test3_uri_querier(self):
        path_input = "test/data/schema_matching/default_matches_cities_input.csv"
        df = pd.read_csv(path_input)

        path_expected = "test/data/schema_matching/default_matches_cities_expected.csv"
        expected_matches = pd.read_csv(path_expected)

        output_matches = relational_matching(df, uri_data_model=True)
        output_matches['value'] = pd.to_numeric(output_matches['value'])

        pd.testing.assert_frame_equal(
            output_matches, expected_matches, check_like=True)

    def test4_uri_querier_no_matches(self):
        path_input = "test/data/schema_matching/no_matches_cities_input.csv"
        df = pd.read_csv(path_input)

        path_expected = "test/data/schema_matching/no_matches_cities_expected.csv"
        expected_matches = pd.read_csv(path_expected)

        output_matches = relational_matching(df, uri_data_model=True)
        output_matches['value'] = pd.to_numeric(output_matches['value'])

        pd.testing.assert_frame_equal(
            output_matches, expected_matches, check_like=True)

    def test5_match_score(self):

        score = 0.76

        path_input = "test/data/schema_matching/default_matches_cities_input.csv"
        df = pd.read_csv(path_input)

        path_expected = "test/data/schema_matching/default_matches_cities_expected.csv"
        expected_matches = pd.read_csv(path_expected)
        expected_matches['value'] = np.where(
            expected_matches['value']==1, score, expected_matches['value'])

        output_matches = relational_matching(df, match_score=score)
        output_matches['value'] = pd.to_numeric(output_matches['value'])

        pd.testing.assert_frame_equal(
            output_matches, expected_matches, check_like=True)

    def test6_one_endpoint(self):

        path_input = "test/data/schema_matching/default_matches_cities_input.csv"
        df = pd.read_csv(path_input)

        path_expected = "test/data/schema_matching/default_matches_cities_expected.csv"
        expected_matches = pd.read_csv(path_expected)

        output_matches = relational_matching(df, endpoints=DBpedia)
        output_matches['value'] = pd.to_numeric(output_matches['value'])

        pd.testing.assert_frame_equal(
            output_matches, expected_matches, check_like=True)

    def test7_no_http_input(self):
        df = pd.DataFrame({'a': [1, 2, 3],
                           'b': [4, 5, 6]})
        expected_matches = pd.DataFrame(columns=["uri_1", "uri_2", "value"])
        output_matches = relational_matching(df)

        pd.testing.assert_frame_equal(
            output_matches, expected_matches, check_like=True)


class TestStringSimilarityMatching():

    def test1_default(self):

        path_input = "test/data/schema_matching/string_matching_input_t1t2.csv"
        df = pd.read_csv(path_input)

        path_expected = "test/data/schema_matching/string_matching_output_t1.csv"
        result_expected = pd.read_csv(path_expected)
        
        result = string_similarity_matching(df, prefix_threshold=1)

        pd.testing.assert_frame_equal(result, result_expected, check_like=True)
        
    def test2_highthreshold(self):

        path_input = "test/data/schema_matching/string_matching_input_t1t2.csv"
        df = pd.read_csv(path_input)

        path_expected = "test/data/schema_matching/string_matching_output_t2.csv"
        result_expected = pd.read_csv(path_expected)
        
        result = string_similarity_matching(df, prefix_threshold=10)

        pd.testing.assert_frame_equal(result, result_expected, check_like=True)
        
    def test3_diffpredicate_diffmetric(self):

        path_input = "test/data/schema_matching/string_matching_input_t3.csv"
        df = pd.read_csv(path_input)

        path_expected = "test/data/schema_matching/string_matching_output_t3.csv"
        result_expected = pd.read_csv(path_expected)
        
        result = string_similarity_matching(df, predicate="dbo:abstract", to_lowercase=False, remove_prefixes=False, remove_punctuation=False, similarity_metric="token_set_levenshtein")

        pd.testing.assert_frame_equal(result, result_expected, check_like=True)


class TestLabelSchemaMatching:
    
    def test1_default(self):
        path_input = "test/data/schema_matching/default_matches_cities_boolean_input.csv"
        df = pd.read_csv(path_input)
        
        path_expected = "test/data/schema_matching/default_matches_cities_boolean_expected.csv"
        expected_matches = pd.read_csv(path_expected)
        
        output_matches = label_schema_matching(df)
        output_matches['same_label'] = pd.to_numeric(output_matches['same_label'])

        pd.testing.assert_frame_equal(
            output_matches, expected_matches, check_like=True)
        
    def test2_no_matches(self):
        path_input = "test/data/schema_matching/no_matches_cities_boolean_input.csv"
        df = pd.read_csv(path_input)
        
        path_expected = "test/data/schema_matching/no_matches_cities_boolean_expected.csv"
        expected_matches = pd.read_csv(path_expected)
        
        output_matches = label_schema_matching(df)
        output_matches['same_label'] = pd.to_numeric(output_matches['same_label'])

        pd.testing.assert_frame_equal(
            output_matches, expected_matches, check_like=True)
        
    def test3_uri_querier(self):
        path_input = "test/data/schema_matching/default_matches_cities_boolean_input.csv"
        df = pd.read_csv(path_input)
        
        path_expected = "test/data/schema_matching/default_matches_cities_boolean_expected.csv"
        expected_matches = pd.read_csv(path_expected)
        
        output_matches = label_schema_matching(df, uri_data_model=True)
        output_matches['same_label'] = pd.to_numeric(output_matches['same_label'])

        pd.testing.assert_frame_equal(
            output_matches, expected_matches, check_like=True)
        
    def test4_uri_querier_no_matches(self):
        path_input = "test/data/schema_matching/no_matches_cities_boolean_input.csv"
        df = pd.read_csv(path_input)
        
        path_expected = "test/data/schema_matching/no_matches_cities_boolean_expected.csv"
        expected_matches = pd.read_csv(path_expected)
        
        output_matches = label_schema_matching(df, uri_data_model=True)
        output_matches['same_label'] = pd.to_numeric(output_matches['same_label'])

        pd.testing.assert_frame_equal(
            output_matches, expected_matches, check_like=True)
        
        
class TestValueOverlapMatching:
    
    def test1_boolean_data(self):
        path_input = "test/data/schema_matching/default_matches_cities_boolean_input.csv"
        df = pd.read_csv(path_input)
        
        path_expected = "test/data/schema_matching/value_matches_cities_boolean_expected.csv"
        expected_matches = pd.read_csv(path_expected)
        
        output_matches = value_overlap_matching(df)
        output_matches['value_overlap'] = pd.to_numeric(output_matches['value_overlap'])

        pd.testing.assert_frame_equal(
            output_matches, expected_matches, check_like=True)
        
    def test2_no_matches_boolean_data(self):
        df = pd.DataFrame({
            'city' : [1, 1, 0, 1],
            'entity' : ['Bremen', 'Hamburg', 'Denmark', 'Berlin'],
            'new_link_1': ['http://dbpedia.org/resource/Bremen', 'http://dbpedia.org/resource/Hamburg', 'http://dbpedia.org/resource/Denmark', 'http://dbpedia.org/resource/Berlin'],
            'new_link_in_boolean_http://dbpedia.org/resource/Category:German_state_capitals': [True, True, False, True],
            'new_link_in_boolean_http://dbpedia.org/resource/Category:Countries_in_Europe': [False, False, True, False]
        })
        
        expected_result_df = pd.DataFrame({
            'uri_1' : ['new_link_in_boolean_http://dbpedia.org/resource/Category:Countries_in_Europe'],
            'uri_2' : ['http://dbpedia.org/resource/Category:German_state_capitals'],
            'value_overlap': [0.0]
        })
        
        result = value_overlap_matching(df)

        pd.testing.assert_frame_equal(
            result, expected_result_df, check_like=True)
        
    def test3_numeric_data(self):
        path_input = "test/data/schema_matching/value_matches_cities_numeric_input.csv"
        df = pd.read_csv(path_input)
        
        path_expected = "test/data/schema_matching/value_matches_cities_numeric_expected.csv"
        expected_matches = pd.read_csv(path_expected)
        
        output_matches = value_overlap_matching(df)
        output_matches['value_overlap'] = pd.to_numeric(output_matches['value_overlap'])

        pd.testing.assert_frame_equal(
            output_matches, expected_matches, check_like=True)
        
    def test4_no_matches_numeric_data(self):
        df = pd.DataFrame({
            'city' : [1, 1, 0, 1],
            'entity' : ['Bremen', 'Hamburg', 'Denmark', 'Berlin'],
            'new_link_1': ['http://dbpedia.org/resource/Bremen', 'http://dbpedia.org/resource/Hamburg', 'http://dbpedia.org/resource/Denmark', 'http://dbpedia.org/resource/Berlin'],
            'Link_Out_numeric_http://dbpedia.org/ontology/PopulatedPlace/areaMetro': [1, 0, 0, 0],
            'Link_Out_numeric_http://dbpedia.org/ontology/abstract': [12, 12, 11, 12]
        })
        
        expected_result_df = pd.DataFrame({
            'uri_1' : ['http://dbpedia.org/ontology/PopulatedPlace/areaMetro'],
            'uri_2' : ['http://dbpedia.org/ontology/abstract'],
            'value_overlap': [0.0]
        })
        
        result = value_overlap_matching(df)

        pd.testing.assert_frame_equal(
            result, expected_result_df, check_like=True)
        
            
class TestSimilarityOfPairs:
    
    def test1_smallset(self):
        path_input = "test/data/schema_matching/default_matches_cities_input.csv"
        df = pd.read_csv(path_input)    

        pairs_relational = relational_matching(df)[["uri_1","uri_2"]].sort_values(by=["uri_1","uri_2"]).reset_index(drop=True)
        pairs_string = string_similarity_matching(df)[["uri_1","uri_2"]].sort_values(by=["uri_1","uri_2"]).reset_index(drop=True)
        pairs_schema = label_schema_matching(df)[["uri_1","uri_2"]].sort_values(by=["uri_1","uri_2"]).reset_index(drop=True)
        pairs_overlap = value_overlap_matching(df)[["uri_1","uri_2"]].sort_values(by=["uri_1","uri_2"]).reset_index(drop=True)

        assert all([pairs_relational.equals(x) for x in [pairs_string, pairs_schema, pairs_overlap]])

    def test2_bigset(self):

        #WARNING: Takes long to run!

        path_input = "test/data/schema_matching/pair_equality_test2_bigset.csv"
        df = pd.read_csv(path_input)    

        pairs_relational = relational_matching(df)[["uri_1","uri_2"]].sort_values(by=["uri_1","uri_2"]).reset_index(drop=True)
        pairs_string = string_similarity_matching(df)[["uri_1","uri_2"]].sort_values(by=["uri_1","uri_2"]).reset_index(drop=True)
        pairs_schema = label_schema_matching(df)[["uri_1","uri_2"]].sort_values(by=["uri_1","uri_2"]).reset_index(drop=True)
        pairs_overlap = value_overlap_matching(df)[["uri_1","uri_2"]].sort_values(by=["uri_1","uri_2"]).reset_index(drop=True)

        assert all([pairs_relational.equals(x) for x in [pairs_string, pairs_schema, pairs_overlap]])


        
    
        
        
        
        