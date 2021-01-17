import pandas as pd
from sklearn.pipeline import Pipeline
import pytest

from kgextension.linking_sklearn import *
from kgextension.generator_sklearn import *
from kgextension.feature_selection_sklearn import *
from kgextension.schema_matching_fusion_sklearn import MatchingFuser
from kgextension.utilities_sklearn import *

class TestOneFunctionPipeline:
    
    def test1_PatternLinker(self):
        input_df = pd.read_csv("test/data/scikit_learn/cities.csv")

        Linker = PatternLinker(column='entity', base_url='http://dbpedia.org/resource/')

        pipeline = Pipeline(steps = [('pattern_linker', Linker)])

        output_df = pipeline.fit_transform(input_df)

        expected_df = pd.read_csv("test\data\scikit_learn\OneFunction_1_expected.csv")

        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
    
    def test2_DbpediaSpotlightLinker(self):
        input_df = pd.read_csv("test/data/scikit_learn/cities.csv")

        Linker = DbpediaSpotlightLinker(column='entity', language="en")
        
        pipeline = Pipeline(steps = [('dbpedia_spotlight_linker', Linker)])

        output_df = pipeline.fit_transform(input_df)

        expected_df = pd.read_csv("test\data\scikit_learn\OneFunction_2_expected.csv")

        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
        
    def test3_DbpediaLookupLinker(self):
        input_df = pd.read_csv("test/data/scikit_learn/cities.csv")

        Linker = DbpediaLookupLinker(column='entity', base_url="http://lookup.dbpedia.org/api/search/")
        
        pipeline = Pipeline(steps = [('dbpedia_lookup_linker', Linker)])

        output_df = pipeline.fit_transform(input_df)

        expected_df = pd.read_csv("test\data\scikit_learn\OneFunction_3_expected.csv")
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
        
        
    def test4_LabelLinker(self):
        input_df = pd.read_csv("test/data/scikit_learn/cities.csv")

        Linker = LabelLinker(column='entity', language="de")
        
        pipeline = Pipeline(steps = [('label_linker', Linker)])

        output_df = pipeline.fit_transform(input_df)

        expected_df = pd.read_csv("test\data\scikit_learn\OneFunction_4_expected.csv")

        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
        
    def test5_SameAsLinker(self):
        input_df = pd.read_csv("test\data\scikit_learn\OneFunction_1_expected.csv")

        Linker = SameAsLinker(column='new_link', new_attribute_name="same_as")
        
        pipeline = Pipeline(steps = [('sameas_linker', Linker)])

        output_df = pipeline.fit_transform(input_df)

        expected_df = pd.read_csv("test\data\scikit_learn\OneFunction_5_expected.csv")

        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
        
                
class TestTwoFunctionsPipeline:
    
    def test1_PatternLinker_SpecificRelationGenerator(self):
        input_df = pd.read_csv("test/data/scikit_learn/cities.csv")

        Linker = PatternLinker(column='entity', base_url='http://dbpedia.org/resource/')
        Checker = CheckUriRedirects(column='new_link', bundled_mode=True, uri_data_model=True)
        Generator = SpecificRelationGenerator(columns='new_link', hierarchy_relation = 'http://www.w3.org/2004/02/skos/core#broader')

        pipeline = Pipeline(steps = [('pattern_linker', Linker),
                                     ('check_uri_redirects', Checker),
                                     ('specific_relation_generator', Generator)])

        output_df = pipeline.fit_transform(input_df)
        
        expected_df = pd.read_csv("test/data/scikit_learn/TwoFunctions_1_expected.csv")
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
        
    def test2_LabelLinker_QualifiedRelationGenerator(self):
        input_df = pd.read_csv("test/data/scikit_learn/cities.csv")
        
        Linker = LabelLinker('entity', language="de")
        Checker = CheckUriRedirects(column='new_link_1', bundled_mode=True, uri_data_model=True)
        Generator = QualifiedRelationGenerator(columns=["new_link_1"], uri_data_model=True, direction="In")

        pipeline = Pipeline(steps = [('label_linker', Linker),
                                     ('check_uri_redirects', Checker),
                                     ('qualified_relation_generator', Generator)])
        
        output_df = pipeline.fit_transform(input_df)
        
        expected_df = pd.read_csv("test/data/scikit_learn/TwoFunctions_2_expected.csv")
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
        
    def test3_LabelLinker_QualifiedRelationGenerator_hierarchy(self):
        input_df = pd.read_csv("test/data/scikit_learn/cities.csv")
        
        Linker = LabelLinker('entity', language="de")
        Checker = CheckUriRedirects(column='new_link_1', bundled_mode=True, uri_data_model=True)
        Generator = QualifiedRelationGenerator(columns=["new_link_1"], uri_data_model=True, direction="In", hierarchy=True)

        pipeline = Pipeline(steps = [('label_linker', Linker),
                                     ('check_uri_redirects', Checker),
                                     ('qualified_relation_generator', Generator)])
        
        output_df = pipeline.fit_transform(input_df)
        
        expected_df = pd.read_csv("test/data/scikit_learn/TwoFunctions_3_expected.csv")
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
        
    def test4_DbpediaSpotlightLinker_UnqualifiedRelationGenerator(self):
        input_df = pd.read_csv("test/data/scikit_learn/cities.csv")
        
        Linker = DbpediaSpotlightLinker(column='entity', language="en")
        Checker = CheckUriRedirects(column='new_link', bundled_mode=True, uri_data_model=True)
        Generator = UnqualifiedRelationGenerator(columns=["new_link"])

        pipeline = Pipeline(steps = [('dbpedia_spotlight_linker', Linker),
                                     ('check_uri_redirects', Checker),
                                     ('unqualified_relation_generator', Generator)])
        
        output_df = pipeline.fit_transform(input_df)
        
        expected_df = pd.read_csv("test/data/scikit_learn/TwoFunctions_4_expected.csv")
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
        
    def test5_DbpediaLookupLinker_DataPropertiesGenerator(self):
        input_df = pd.read_csv("test/data/scikit_learn/cities.csv")
        
        Linker = DbpediaLookupLinker(column='entity', base_url="http://lookup.dbpedia.org/api/search/")
        Checker = CheckUriRedirects(column='new_link', bundled_mode=True, uri_data_model=True)
        Generator = DataPropertiesGenerator(columns=["new_link"])

        pipeline = Pipeline(steps = [('dbpedia_lookup_linker', Linker),
                                     ('check_uri_redirects', Checker),
                                     ('data_properties_generator', Generator)])
        
        output_df = pipeline.fit_transform(input_df)
        
        expected_df = pd.read_csv("test/data/scikit_learn/TwoFunctions_5_expected.csv")
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
        
    def test6_DbpediaLookupLinker_SameAsLinker(self):
        input_df = pd.read_csv("test/data/scikit_learn/cities.csv")

        Linker = DbpediaLookupLinker(column='entity', base_url="http://lookup.dbpedia.org/api/search/")
        SameAsLinker = SameAsLinker(column='new_link', new_attribute_name="same_as")
        
        pipeline = Pipeline(steps = [('dbpedia_lookup_linker', Linker),
                                     ('sameas_linker', SameAsLinker)])

        output_df = pipeline.fit_transform(input_df)

        expected_df = pd.read_csv("test/data/scikit_learn/TwoFunctions_6_expected.csv")

        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
        
        
    def test7_DbpediaSpotlightLinker_DirectTypeGenerator(self):
        input_df = pd.read_csv("test/data/scikit_learn/cities.csv")
        
        Linker = DbpediaSpotlightLinker(column='entity', language="en")
        Checker = CheckUriRedirects(column='new_link', bundled_mode=True, uri_data_model=False)
        Generator = DirectTypeGenerator(columns=["new_link"])

        pipeline = Pipeline(steps = [('dbpedia_spotlight_linker', Linker),
                                     ('check_uri_redirects', Checker),
                                     ('direct_type_generator', Generator)])
        
        output_df = pipeline.fit_transform(input_df)
        
        expected_df = pd.read_csv("test/data/scikit_learn/TwoFunctions_7_expected.csv")
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
        
        
class TestTreeFunctionsPineline:
    
    def test1_PatternLinker_SpecificRelationGenerator_HillClimbingFilter(self):
        input_df = pd.read_csv("test/data/scikit_learn/cities.csv")

        Linker = PatternLinker(column='entity', base_url='http://dbpedia.org/resource/')
        Checker = CheckUriRedirects(column='new_link')
        Generator = SpecificRelationGenerator(columns='new_link', hierarchy_relation = 'http://www.w3.org/2004/02/skos/core#broader')
        Filter = HillClimbingFilter(label_column='city')

        pipeline = Pipeline(steps = [('pattern_linker', Linker),
                                     ('check_uri_redirects', Checker),
                                     ('specific_relation_generator', Generator),
                                     ('hill_climbing_filter', Filter)])

        output_df = pipeline.fit_transform(input_df)
        
        expected_df = pd.read_csv("test\data\scikit_learn\ThreeFunctions_1_expected.csv")
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)

    def test2_DbpediaSpotlightLinker_DirectTypeGenerator_HierarchyBasedFilter(self):
        input_df = pd.read_csv("test/data/scikit_learn/cities.csv")
        
        Linker = DbpediaSpotlightLinker(column='entity', language="en")
        Checker = CheckUriRedirects(column='new_link', bundled_mode=True, uri_data_model=False)
        Generator = DirectTypeGenerator(columns=["new_link"], uri_data_model=True, regex_filter=["wikidata"], hierarchy=True)
        Filter = HierarchyBasedFilter(label_column="city", G=None)

        pipeline = Pipeline(steps = [('dbpedia_spotlight_linker', Linker),
                                     ('check_uri_redirects', Checker),
                                     ('direct_type_generator', Generator),
                                     ('hierarchy_based_filter', Filter)])
        
        output_df = pipeline.fit_transform(input_df)
        
        expected_df = pd.read_csv("test\data\scikit_learn\ThreeFunctions_2_expected.csv")
        
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)

    def test3_DbpediaSpotlightLinker_DirectTypeGenerator_GreedyTopDownFilter(self):
        input_df = pd.read_csv("test/data/scikit_learn/cities.csv")
        
        Linker = DbpediaSpotlightLinker(column='entity', language="en")
        Checker = CheckUriRedirects(column='new_link', bundled_mode=True, uri_data_model=False)
        Generator = DirectTypeGenerator(columns=["new_link"], uri_data_model=True, regex_filter=["wikidata"], hierarchy=True)
        Filter = GreedyTopDownFilter(label_column='city', column_prefix = "new_link_type_")

        pipeline = Pipeline(steps = [('dbpedia_spotlight_linker', Linker),
                                     ('check_uri_redirects', Checker),
                                     ('direct_type_generator', Generator),
                                     ('greedy_top_down_filter', Filter)])
        
        output_df = pipeline.fit_transform(input_df)
        
        expected_df = pd.read_csv("test\data\scikit_learn\ThreeFunctions_3_expected.csv")
 
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)
    
    def test4_DbpediaLookupLinker_DirectTypeGenerator_TreeBasedFilter(self):
        input_df = pd.read_csv("test/data/scikit_learn/cities.csv")
        
        Linker = DbpediaLookupLinker(column='entity', base_url="http://lookup.dbpedia.org/api/search/")
        Checker = CheckUriRedirects(column='new_link', bundled_mode=True, uri_data_model=True)
        Generator = DirectTypeGenerator(columns=["new_link"], uri_data_model=True, regex_filter=["wikidata"], hierarchy=True)
        Filter = TreeBasedFilter(label_column='city', G=None, metric="Lift")
        
        pipeline = Pipeline(steps = [('dbpedia_lookup_linker', Linker),             
                                     ('check_uri_redirects', Checker),
                                     ('direct_type_generator', Generator),
                                     ('tree_based_filter', Filter)])
        
        output_df = pipeline.fit_transform(input_df)
        
        expected_df = pd.read_csv("test\data\scikit_learn\ThreeFunctions_4_expected.csv")
 
        pd.testing.assert_frame_equal(output_df, expected_df, check_like=True)

        
        






