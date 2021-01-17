import pandas as pd
import pytest
from kgextension.link_exploration import link_explorer

class TestLinkExplorer:

    def test1_default(self):
        df_input = pd.read_csv("test/data/link_exploration/link_exploration_test_input.csv")
        expected_result = pd.read_csv("test/data/link_exploration/link_exploration_test1_expected.csv")

        result = link_explorer(df_input, "uri")

        pd.testing.assert_frame_equal(result, expected_result, check_like = True)
    
    def test2_multiple_hops(self):
        df_input = pd.read_csv("test/data/link_exploration/link_exploration_test_input.csv")
        expected_result = pd.read_csv("test/data/link_exploration/link_exploration_test2_expected.csv")

        result = link_explorer(df_input, "uri", number_of_hops=3)

        pd.testing.assert_frame_equal(result, expected_result, check_like = True)
    
    def test3_multiple_links_to_follow(self):
        df_input = pd.read_csv("test/data/link_exploration/link_exploration_test_input.csv")
        expected_result = pd.read_csv("test/data/link_exploration/link_exploration_test3_expected.csv")

        result = link_explorer(df_input, "uri", links_to_follow=["owl:sameAs","rdfs:seeAlso"])

        pd.testing.assert_frame_equal(result, expected_result, check_like = True)
    
    def test4_lod_source(self):
        df_input = pd.read_csv("test/data/link_exploration/link_exploration_test_input.csv")
        expected_result = pd.read_csv("test/data/link_exploration/link_exploration_test4_expected.csv")

        result = link_explorer(df_input, "uri", lod_sources=["nytimes","geonames"])

        pd.testing.assert_frame_equal(result, expected_result, check_like = True)

    def test5_prefix_lookup(self):
        df_input = pd.read_csv("test/data/link_exploration/link_exploration_test_input.csv")
        expected_result = pd.read_csv("test/data/link_exploration/link_exploration_test5_expected.csv")
        prefixes = {"irgendeinprefix" : "http://www.w3.org/2002/07/owl#"}

        result = link_explorer(df_input, "uri", links_to_follow=["irgendeinprefix:sameAs"],prefix_lookup=prefixes)

        pd.testing.assert_frame_equal(result, expected_result, check_like = True)
    
    def test6_exclude_source(self):
        df_input = pd.read_csv("test/data/link_exploration/link_exploration_test_input.csv")
        expected_result = pd.read_csv("test/data/link_exploration/link_exploration_test6_expected.csv")

        result = link_explorer(df_input, "uri", exclude_sources=["dbpedia"])

        pd.testing.assert_frame_equal(result, expected_result, check_like = True)
    
    def test7_empty_result(self):
        df_input = pd.read_csv("test/data/link_exploration/link_exploration_test_input.csv")
        expected_result = pd.read_csv("test/data/link_exploration/link_exploration_test7_expected.csv")

        result = link_explorer(df_input, "uri", links_to_follow=["funkioniert:nicht"])

        pd.testing.assert_frame_equal(result, expected_result, check_like = True)