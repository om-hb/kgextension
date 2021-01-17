import pandas as pd
import networkx as nx
import pytest
from kgextension.feature_selection import hill_climbing_filter, hierarchy_based_filter, tree_based_filter
from kgextension.generator import specific_relation_generator, direct_type_generator

class TestHillCLimbingFilter:

    def test1_high_beta(self):

        input_df = pd.read_csv("test/data/feature_selection/hill_climbing_test1_input.csv")

        input_DG = nx.DiGraph()
        labels = ['http://chancellor', 'http://president', 'http://European_politician', 
                  'http://head_of_state', 'http://politician', 'http://man', 'http://person', 'http://being']
        input_DG.add_nodes_from(labels)
        input_DG.add_edges_from([('http://chancellor', 'http://politician'), ('http://president', 'http://politician'),
        ('http://chancellor', 'http://head_of_state'), ('http://president', 'http://head_of_state'), ('http://head_of_state', 'http://person'),
        ('http://European_politician', 'http://politician'), ('http://politician', 'http://person'),
        ('http://man', 'http://person'), ('http://person', 'http://being')])

        expected_df = pd.read_csv("test/data/feature_selection/hill_climbing_test1_expected.csv")

        output_df = hill_climbing_filter(input_df, 'uri_bool_http://class', G= input_DG, beta=0.5, k=2)

        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)

    def test2_generator_data_low_beta(self):
        
        df = pd.DataFrame({
             'entities': ['Paris', 'Buenos Aires', 'Mannheim', "München"],
             'link': ['http://dbpedia.org/resource/Paris', 'http://dbpedia.org/resource/Buenos_Aires',
                      'http://dbpedia.org/resource/Mannheim', 'http://dbpedia.org/resource/Munich']
            })
        input_df = specific_relation_generator(
            df, columns=['link'], hierarchy_relation='http://www.w3.org/2004/02/skos/core#broader')

        expected_df = pd.read_csv("test/data/feature_selection/hill_climbing_test2_expected.csv")              
        
        output_df = hill_climbing_filter(input_df, 'link_in_boolean_http://dbpedia.org/resource/Category:Prefectures_in_France', beta=0.05, k=3)
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)

    def test3_nan(self):

        input_df = pd.read_csv("test/data/feature_selection/hill_climbing_test3_input.csv")

        input_DG = nx.DiGraph()
        labels = ['http://chancellor', 'http://president', 'http://European_politician', 
                  'http://head_of_state', 'http://politician', 'http://man', 'http://person', 'http://being']
        input_DG.add_nodes_from(labels)
        input_DG.add_edges_from([('http://chancellor', 'http://politician'), ('http://president', 'http://politician'),
        ('http://chancellor', 'http://head_of_state'), ('http://president', 'http://head_of_state'), ('http://head_of_state', 'http://person'),
        ('http://European_politician', 'http://politician'), ('http://politician', 'http://person'),
        ('http://man', 'http://person'), ('http://person', 'http://being')])

        expected_df = pd.read_csv("test/data/feature_selection/hill_climbing_test3_expected.csv")

        output_df = hill_climbing_filter(input_df, 'class', G= input_DG, beta=0.5, k=2)
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)


    def test4_callable_function(self):

        input_df = pd.read_csv("test/data/feature_selection/hill_climbing_test1_input.csv")

        input_DG = nx.DiGraph()
        labels = ['http://chancellor', 'http://president', 'http://European_politician', 
                  'http://head_of_state', 'http://politician', 'http://man', 'http://person', 'http://being']
        input_DG.add_nodes_from(labels)
        input_DG.add_edges_from([('http://chancellor', 'http://politician'), ('http://president', 'http://politician'),
        ('http://chancellor', 'http://head_of_state'), ('http://president', 'http://head_of_state'), ('http://head_of_state', 'http://person'),
        ('http://European_politician', 'http://politician'), ('http://politician', 'http://person'),
        ('http://man', 'http://person'), ('http://person', 'http://being')])

        def fake_metric(df, class_col, param=5):
            return 1/((df.sum(axis=1)*class_col).sum()/param)
    
        expected_df = pd.read_csv("test/data/feature_selection/hill_climbing_test4_expected.csv")
        
        output_df = hill_climbing_filter(input_df, 'uri_bool_http://class', metric=fake_metric, G= input_DG, param=6)
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)

    def test5_no_graph(self):

        input_df = pd.read_csv("test/data/feature_selection/hill_climbing_test3_input.csv")

        with pytest.raises(RuntimeError) as excinfo:
            _ = hill_climbing_filter(input_df, 'class', beta=0.5, k=2)

        assert "df.attrs['hierarchy]" in str(excinfo.value)
    

class TestHierarchyBasedFilter():
    
    def test1_no_pruning_info_gain_with_G(self):
        
        df = pd.DataFrame({
            'entities': ['Paris', 'Buenos Aires', 'Mannheim', "München"],
            'link': ['http://dbpedia.org/resource/Paris', 'http://dbpedia.org/resource/Buenos_Aires',
                     'http://dbpedia.org/resource/Mannheim', 'http://dbpedia.org/resource/Munich']
            })
        
        expected_df = pd.read_csv("test\data\feature_selection\hierarchy_based_test1_expected.csv")

        input_df = direct_type_generator(df, ["link"], regex_filter=['A'], result_type="boolean", bundled_mode=True, hierarchy=True)
        
        input_DG = input_df.attrs['hierarchy']
        
        output_df = hierarchy_based_filter(input_df, "link", threshold=0.99, G=input_DG, metric="info_gain", pruning=False)
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
        
    def test2_no_pruning_correlation(self):
        
        df = pd.DataFrame({
            'entities': ['Paris', 'Buenos Aires', 'Mannheim', "München"],
            'link': ['http://dbpedia.org/resource/Paris', 'http://dbpedia.org/resource/Buenos_Aires',
                     'http://dbpedia.org/resource/Mannheim', 'http://dbpedia.org/resource/Munich']
            })
        
        expected_df = pd.read_csv("test\data\feature_selection\hierarchy_based_test2_expected.csv")
        
        input_df = direct_type_generator(df, ["link"], regex_filter=['A'], result_type="boolean", bundled_mode=True, hierarchy=True)
        
        output_df = hierarchy_based_filter(input_df, "link", threshold=0.99, G=input_DG, metric="correlation", pruning=False)
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
        
    def test3_pruning_info_gain_all_remove_True(self):
        
        df = pd.DataFrame({
            'entities': ['Paris', 'Buenos Aires', 'Mannheim', "München"],
            'link': ['http://dbpedia.org/resource/Paris', 'http://dbpedia.org/resource/Buenos_Aires',
                     'http://dbpedia.org/resource/Mannheim', 'http://dbpedia.org/resource/Munich']
            })
        
        expected_df = pd.read_csv("test\data\feature_selection\hierarchy_based_test3_expected.csv")
        
        input_df = direct_type_generator(df, ["link"], regex_filter=['A'], result_type="boolean", bundled_mode=True, hierarchy=True)
        
        input_DG = input_df.attrs['hierarchy']
    
        output_df = hierarchy_based_filter(input_df, "link", G=input_DG, threshold=0.99, metric="info_gain", pruning=True)
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
        
    def test4_pruning_correlation_all_remove_True(self):
        
        df = pd.DataFrame({
            'entities': ['Paris', 'Buenos Aires', 'Mannheim', "München"],
            'link': ['http://dbpedia.org/resource/Paris', 'http://dbpedia.org/resource/Buenos_Aires',
                     'http://dbpedia.org/resource/Mannheim', 'http://dbpedia.org/resource/Munich']
            })
        
        expected_df = pd.read_csv("test\data\feature_selection\hierarchy_based_test4_expected.csv")

        input_df = direct_type_generator(df, ["link"], regex_filter=['A'], result_type="boolean", bundled_mode=True, hierarchy=True)
        
        input_DG = input_df.attrs['hierarchy']

        output_df = hierarchy_based_filter(input_df, "link", G=input_DG, threshold=0.99, metric="correlation", pruning=True)
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like = True)
        
    def test5_pruning_info_gain_all_remove_False(self):
        
        df = pd.DataFrame({
            'entities': ['Paris', 'Buenos Aires', 'Mannheim', "München"],
            'link': ['http://dbpedia.org/resource/Paris', 'http://dbpedia.org/resource/Buenos_Aires',
                     'http://dbpedia.org/resource/Mannheim', 'http://dbpedia.org/resource/Munich']
            })
        
        expected_df = pd.read_csv("test\data\feature_selection\hierarchy_based_test5_expected.csv")

        input_df = direct_type_generator(df, ["link"], regex_filter=['A'], result_type="boolean", bundled_mode=True, hierarchy=True)
        
        input_DG = input_df.attrs['hierarchy']

        output_df = hierarchy_based_filter(input_df, "link", G=input_DG, threshold=0.99, metric="info_gain", pruning=True, all_remove=False)
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like = True)
        
    def test6_pruning_correlation_all_remove_False(self):
        
        df = pd.DataFrame({
            'entities': ['Paris', 'Buenos Aires', 'Mannheim', "München"],
            'link': ['http://dbpedia.org/resource/Paris', 'http://dbpedia.org/resource/Buenos_Aires',
                     'http://dbpedia.org/resource/Mannheim', 'http://dbpedia.org/resource/Munich']
            })
        
        expected_df = pd.read_csv("test\data\feature_selection\hierarchy_based_test6_expected.csv")

        input_df = direct_type_generator(df, ["link"], regex_filter=['A'], result_type="boolean", bundled_mode=True, hierarchy=True)
        
        input_DG = input_df.attrs['hierarchy']
        
        output_df = hierarchy_based_filter(input_df, "link", G=input_DG, threshold=0.99, metric="correlation", pruning=True, 
                                           all_remove=False)
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like = True)
    
    
    def test7_no_input_G(self):
        
        df = pd.DataFrame({
            'entities': ['Paris', 'Buenos Aires', 'Mannheim', "München"],
            'link': ['http://dbpedia.org/resource/Paris', 'http://dbpedia.org/resource/Buenos_Aires',
                     'http://dbpedia.org/resource/Mannheim', 'http://dbpedia.org/resource/Munich']
            })
        
        expected_df = pd.read_csv("test\data\feature_selection\hierarchy_based_test7_expected.csv")

        input_df = direct_type_generator(df, ["link"], regex_filter=['A'], result_type="boolean", bundled_mode=True, hierarchy=True)
        
        output_df = hierarchy_based_filter(input_df, "link", threshold=0.99, metric="correlation", pruning=True, 
                                           all_remove=False)
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like = True)
        
    def test8_nan(self):

        input_df = pd.read_csv("test/data/feature_selection/hill_climbing_test3_input.csv")

        input_DG = nx.DiGraph()
        labels = ['http://chancellor', 'http://president', 'http://European_politician', 
                  'http://head_of_state', 'http://politician', 'http://man', 'http://person', 'http://being']
        input_DG.add_nodes_from(labels)
        input_DG.add_edges_from([('http://chancellor', 'http://politician'), ('http://president', 'http://politician'),
        ('http://chancellor', 'http://head_of_state'), ('http://president', 'http://head_of_state'), ('http://head_of_state', 'http://person'),
        ('http://European_politician', 'http://politician'), ('http://politician', 'http://person'),
        ('http://man', 'http://person'), ('http://person', 'http://being')])

        expected_df = pd.read_csv("test/data/feature_selection/hierarchy_based_test8_expected.csv")

        output_df = hierarchy_based_filter(input_df, 'class', G=input_DG, threshold=0.99, metric="info_gain", pruning=True)
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
    
    def test9_callable_function(self):
        
        input_df = pd.read_csv("test/data/feature_selection/hill_climbing_test1_input.csv")

        input_DG = nx.DiGraph()
        labels = ['http://chancellor', 'http://president', 'http://European_politician', 
                  'http://head_of_state', 'http://politician', 'http://man', 'http://person', 'http://being']
        input_DG.add_nodes_from(labels)
        input_DG.add_edges_from([('http://chancellor', 'http://politician'), ('http://president', 'http://politician'),
        ('http://chancellor', 'http://head_of_state'), ('http://president', 'http://head_of_state'), ('http://head_of_state', 'http://person'),
        ('http://European_politician', 'http://politician'), ('http://politician', 'http://person'),
        ('http://man', 'http://person'), ('http://person', 'http://being')])

        def fake_metric(df_from_hierarchy, l, d):
            equivalence = df_from_hierarchy[l] == df_from_hierarchy[d]
            return equivalence.sum()/len(equivalence)
    
        expected_df = pd.read_csv("test/data/feature_selection/hierarchy_based_test9_expected.csv")
        
        output_df = hierarchy_based_filter(input_df, 'uri_bool_http://class', G= input_DG, threshold=0.99, metric=fake_metric, pruning=True)
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
        

class TestTreeBasedFilter:

    def test1_lift(self):

        input_df = pd.read_csv("test/data/feature_selection/tree_based_test_input.csv")

        input_df_dt = direct_type_generator(input_df, ['uri'], hierarchy=True)

        expected_df = pd.read_csv("test/data/feature_selection/tree_based_test1_expected.csv")

        output_df = tree_based_filter(input_df_dt, 'europe', metric='Lift')

        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)

    def test2_ig(self):

        input_df = pd.read_csv("test/data/feature_selection/tree_based_test_input.csv")

        input_df_dt = direct_type_generator(input_df, ['uri'], hierarchy=True)

        expected_df = pd.read_csv("test/data/feature_selection/tree_based_test2_expected.csv")

        output_df = tree_based_filter(input_df_dt, 'europe', metric='IG')

        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
        




    
                
    

