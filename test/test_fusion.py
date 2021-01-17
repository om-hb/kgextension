import pandas as pd
import numpy as np
import pytest

from kgextension.fusion import data_fuser, get_fusion_clusters
from kgextension.schema_matching import relational_matching, string_similarity_matching, value_overlap_matching, matching_combiner


class TestDataFuser:

    def test1_default_boolean(self):

        input_df = pd.read_csv("test/data/fusion/input_df_test1.csv")
        input_df = input_df.astype({'new_link_in_boolean_http://www.wikidata.org/entity/Q4587626': bool})
        input_matches = pd.read_csv("test/data/fusion/input_matches_test1.csv")
        clusters = get_fusion_clusters(input_matches, threshold=0.85)

        df_expected = pd.read_csv("test/data/fusion/fused_expected_test1.csv")

        output_fused = data_fuser(input_df, clusters)

        pd.testing.assert_frame_equal(
            output_fused, df_expected)

    def test2_default_numeric(self):

        input_df = pd.read_csv("test/data/fusion/input_df_test2.csv")
        clusters = [set(['http://a', 'http://b', 'http://c']),
                    set(['http://d', 'http://e']),
                    set(['http://f', 'http://g', 'http://h'])]

        df_expected = pd.read_csv("test/data/fusion/fused_expected_test2.csv")

        output_fused = data_fuser(input_df, clusters)

        pd.testing.assert_frame_equal(
            output_fused, df_expected, check_like=True)

    def test3_default_string(self):

            input_df = pd.read_csv("test/data/fusion/input_df_test3.csv")
            clusters = [set(['http://a', 'http://b', 'http://c']),
                        set(['http://d', 'http://e']),
                        set(['http://f', 'http://g', 'http://h'])]

            df_expected = pd.read_csv("test/data/fusion/fused_expected_test3.csv")

            output_fused = data_fuser(input_df, clusters)

            pd.testing.assert_frame_equal(
                output_fused, df_expected, check_like=True)

    def test4_callable_function(self):

            input_df = pd.read_csv("test/data/fusion/input_df_test3.csv")
            clusters = [set(['http://a', 'http://b', 'http://c']),
                        set(['http://d', 'http://e']),
                        set(['http://f', 'http://g', 'http://h'])]

            df_expected = pd.read_csv("test/data/fusion/fused_expected_test4.csv")

            def own_function(x):
                x = x.dropna()
                if x.empty:
                    return np.nan
                else:
                    return x.sum()

            output_fused = data_fuser(input_df, clusters, string_method_multiple=own_function)

            pd.testing.assert_frame_equal(
                output_fused, df_expected, check_like=True)

