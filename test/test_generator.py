import pandas as pd
import numpy as np
import networkx as nx
import pytest
from kgextension.endpoints import EUOpenData, DBpedia
from kgextension.generator import (
    specific_relation_generator,
    direct_type_generator,
    unqualified_relation_generator, 
    qualified_relation_generator,
    custom_sparql_generator,
    data_properties_generator
)


class TestDirectTypeGenerator:

    def test1_dbpedia_boolean(self):

        df = pd.DataFrame({
            "label": ["Explorair", "Rhein-Flugzeugbau", "Buxton Watermill"], 
            "uri": ["http://dbpedia.org/resource/Explorair", "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_Watermill"]
            })

        expected_result_df = pd.DataFrame({
                    "label": ["Explorair", "Rhein-Flugzeugbau", "Buxton Watermill"], 
                    "uri": ["http://dbpedia.org/resource/Explorair", "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_Watermill"],
                    "uri_type_http://www.w3.org/2002/07/owl#Thing": [True, True, True],
                    "uri_type_http://dbpedia.org/ontology/Company": [True, True, False],
                    "uri_type_http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Agent": [True, True, False],
                    "uri_type_http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#SocialPerson": [True, True, False],
                    "uri_type_http://www.wikidata.org/entity/Q24229398": [True, True, False],
                    "uri_type_http://www.wikidata.org/entity/Q43229": [True, True, False],
                    "uri_type_http://dbpedia.org/ontology/Agent": [True, True, False],
                    "uri_type_http://dbpedia.org/ontology/Organisation": [True, True, False],
                    "uri_type_http://schema.org/Organization": [True, True, False],
                    "uri_type_http://dbpedia.org/ontology/Place": [False, False, True],
                    "uri_type_http://dbpedia.org/ontology/Location": [False, False, True],
                    "uri_type_http://www.w3.org/2003/01/geo/wgs84_pos#SpatialThing": [False, False, True],
                    "uri_type_http://schema.org/Place": [False, False, True]
        })

        result = direct_type_generator(df, "uri", result_type = "boolean", bundled_mode=True)

        pd.testing.assert_frame_equal(result, expected_result_df, check_like = True)


    def test2_dbpedia_boolean_unbundled_multiplefilter(self):

        df = pd.DataFrame({
            "label": ["Explorair", "Rhein-Flugzeugbau", "Buxton Watermill"], 
            "uri": ["http://dbpedia.org/resource/Explorair", "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_Watermill"]
            })

        expected_result_df = pd.DataFrame({
                    "label": ["Explorair", "Rhein-Flugzeugbau", "Buxton Watermill"], 
                    "uri": ["http://dbpedia.org/resource/Explorair", "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_Watermill"],
                    "uri_type_http://www.w3.org/2002/07/owl#Thing": [True, True, True],
                    "uri_type_http://schema.org/Organization": [True, True, False],
                    "uri_type_http://www.w3.org/2003/01/geo/wgs84_pos#SpatialThing": [False, False, True],
                    "uri_type_http://schema.org/Place": [False, False, True]
        })

        result = direct_type_generator(df, ["uri"], result_type = "boolean", bundled_mode=False, regex_filter=["w3.org", "schema.org"])

        pd.testing.assert_frame_equal(result, expected_result_df, check_like = True)


    def test3_dbpedia_boolean_brokenlink(self):

        df = pd.DataFrame({
            "label": ["Explorair", "Rhein-Flugzeugbau", "Buxton Watermill"], 
            "uri": ["http://dbpedia.org/resource/Explorair", "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_WatermillXX"]
            })

        expected_result_df = pd.DataFrame({
                    "label": ["Explorair", "Rhein-Flugzeugbau", "Buxton Watermill"], 
                    "uri": ["http://dbpedia.org/resource/Explorair", "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_WatermillXX"],
                    "uri_type_http://www.w3.org/2002/07/owl#Thing": [True, True, False],
                    "uri_type_http://dbpedia.org/ontology/Company": [True, True, False],
                    "uri_type_http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Agent": [True, True, False],
                    "uri_type_http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#SocialPerson": [True, True, False],
                    "uri_type_http://www.wikidata.org/entity/Q24229398": [True, True, False],
                    "uri_type_http://www.wikidata.org/entity/Q43229": [True, True, False],
                    "uri_type_http://dbpedia.org/ontology/Agent": [True, True, False],
                    "uri_type_http://dbpedia.org/ontology/Organisation": [True, True, False],
                    "uri_type_http://schema.org/Organization": [True, True, False]
        })

        result = direct_type_generator(df, ["uri"], result_type = "boolean", bundled_mode=True)

        pd.testing.assert_frame_equal(result, expected_result_df, check_like = True)


    def test4_dbpedia_boolean_unbundled_brokenlink_nofill(self):

        df = pd.DataFrame({
            "label": ["Explorair", "Rhein-Flugzeugbau", "Buxton Watermill"], 
            "uri": ["http://dbpedia.org/resource/Explorair", "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_WatermillXX"]
            })

        expected_result_df = pd.DataFrame({
                    "label": ["Explorair", "Rhein-Flugzeugbau", "Buxton Watermill"], 
                    "uri": ["http://dbpedia.org/resource/Explorair", "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_WatermillXX"],
                    "uri_type_http://www.w3.org/2002/07/owl#Thing": [True, True, False],
                    "uri_type_http://dbpedia.org/ontology/Company": [True, True, False],
                    "uri_type_http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Agent": [True, True, False],
                    "uri_type_http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#SocialPerson": [True, True, False],
                    "uri_type_http://www.wikidata.org/entity/Q24229398": [True, True, False],
                    "uri_type_http://www.wikidata.org/entity/Q43229": [True, True, False],
                    "uri_type_http://dbpedia.org/ontology/Agent": [True, True, False],
                    "uri_type_http://dbpedia.org/ontology/Organisation": [True, True, False],
                    "uri_type_http://schema.org/Organization": [True, True, False]
        })

        result = direct_type_generator(df, ["uri"], result_type = "boolean", bundled_mode=True)

        pd.testing.assert_frame_equal(result, expected_result_df, check_like = True)


    def test5_dbpedia_boolean_multipleinputs_brokenlink_missing(self):

        df = pd.DataFrame({
            "label": ["Explorair", "Rhein-Flugzeugbau", "Buxton Watermill"], 
            "uri1": ["http://dbpedia.org/resource/Explorair", "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_WatermillXX"],
            "uri2": [np.nan, "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_Watermill"]
            })

        expected_result_df = pd.DataFrame({
                    "label": ["Explorair", "Rhein-Flugzeugbau", "Buxton Watermill"], 
                    "uri1": ["http://dbpedia.org/resource/Explorair", "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_WatermillXX"],
                    "uri2": [np.nan, "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_Watermill"],
                    "type_http://www.w3.org/2002/07/owl#Thing": [True, True, True],
                    "type_http://dbpedia.org/ontology/Company": [True, True, False],
                    "type_http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Agent": [True, True, False],
                    "type_http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#SocialPerson": [True, True, False],
                    "type_http://www.wikidata.org/entity/Q24229398": [True, True, False],
                    "type_http://www.wikidata.org/entity/Q43229": [True, True, False],
                    "type_http://dbpedia.org/ontology/Agent": [True, True, False],
                    "type_http://dbpedia.org/ontology/Organisation": [True, True, False],
                    "type_http://schema.org/Organization": [True, True, False],
                    "type_http://dbpedia.org/ontology/Location": [False, False, True],
                    "type_http://dbpedia.org/ontology/Place": [False, False, True],
                    "type_http://schema.org/Place": [False, False, True],
                    "type_http://www.w3.org/2003/01/geo/wgs84_pos#SpatialThing": [False, False, True]
        })

        result = direct_type_generator(df, ["uri1", "uri2"], result_type = "boolean", bundled_mode=True, endpoint=DBpedia)

        pd.testing.assert_frame_equal(result, expected_result_df, check_like = True)


    def test6_dbpedia_boolean_multipleinputs_brokenlink_missing_uridatamodel(self):

        df = pd.DataFrame({
            "label": ["Explorair", "Rhein-Flugzeugbau", "Buxton Watermill"], 
            "uri1": ["http://dbpedia.org/resource/Explorair", "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_WatermillXX"],
            "uri2": [np.nan, "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_Watermill"]
            })

        expected_result_df = pd.DataFrame({
                    "label": ["Explorair", "Rhein-Flugzeugbau", "Buxton Watermill"], 
                    "uri1": ["http://dbpedia.org/resource/Explorair", "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_WatermillXX"],
                    "uri2": [np.nan, "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_Watermill"],
                    "type_http://www.w3.org/2002/07/owl#Thing": [True, True, True],
                    "type_http://dbpedia.org/ontology/Company": [True, True, False],
                    "type_http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Agent": [True, True, False],
                    "type_http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#SocialPerson": [True, True, False],
                    "type_http://www.wikidata.org/entity/Q24229398": [True, True, False],
                    "type_http://www.wikidata.org/entity/Q43229": [True, True, False],
                    "type_http://dbpedia.org/ontology/Agent": [True, True, False],
                    "type_http://dbpedia.org/ontology/Organisation": [True, True, False],
                    "type_http://schema.org/Organization": [True, True, False],
                    "type_http://dbpedia.org/ontology/Location": [False, False, True],
                    "type_http://dbpedia.org/ontology/Place": [False, False, True],
                    "type_http://schema.org/Place": [False, False, True],
                    "type_http://www.w3.org/2003/01/geo/wgs84_pos#SpatialThing": [False, False, True]
        })

        result = direct_type_generator(df, ["uri1", "uri2"], result_type = "boolean", bundled_mode=True, uri_data_model=True)

        pd.testing.assert_frame_equal(result, expected_result_df, check_like = True)


    def test7_eurostat_boolean(self):

        df = pd.DataFrame({
            "label": ["Element 1", "Element 2", "Element 3"], 
            "uri": ["http://data.europa.eu/4rx/ABB2018/SEC301_01_01", "http://data.europa.eu/4rx/ABB2018/SEC301_01_02_01", "http://data.europa.eu/4rx/ABB2018/SEC301_02_77_01"]
            })

        expected_result_df = pd.DataFrame({
            "label": ["Element 1", "Element 2", "Element 3"], 
            "uri": ["http://data.europa.eu/4rx/ABB2018/SEC301_01_01", "http://data.europa.eu/4rx/ABB2018/SEC301_01_02_01", "http://data.europa.eu/4rx/ABB2018/SEC301_02_77_01"],
            "uri_type_http://data.europa.eu/bud#Article": [True, False, False],
            "uri_type_http://data.europa.eu/3rx#Article": [True, False, False],
            "uri_type_http://data.europa.eu/bud#Item": [False, True, True],
            "uri_type_http://data.europa.eu/3rx#Item": [False, True, True]
            })

        result = direct_type_generator(df, ["uri"], result_type = "boolean", bundled_mode=True, endpoint=EUOpenData)

        pd.testing.assert_frame_equal(result, expected_result_df, check_like = True)


    def test8_eurostat_count_multipleinputs(self):

        df = pd.DataFrame({
            "label": ["Element 1", "Element 2", "Element 3"], 
            "uri1": ["http://data.europa.eu/4rx/ABB2018/SEC301_01_01", "http://data.europa.eu/4rx/ABB2018/SEC301_01_02_01", "http://data.europa.eu/4rx/ABB2018/SEC301_02_77_01"],
            "uri2": ["http://data.europa.eu/4rx/ABB2018/SEC301_03_02", "http://data.europa.eu/4rx/ABB2018/SEC301_02", "http://data.europa.eu/4rx/ABB2018/SEC301_01_03"]
            })

        expected_result_df = pd.DataFrame({
            "label": ["Element 1", "Element 2", "Element 3"], 
            "uri1": ["http://data.europa.eu/4rx/ABB2018/SEC301_01_01", "http://data.europa.eu/4rx/ABB2018/SEC301_01_02_01", "http://data.europa.eu/4rx/ABB2018/SEC301_02_77_01"],
            "uri2": ["http://data.europa.eu/4rx/ABB2018/SEC301_03_02", "http://data.europa.eu/4rx/ABB2018/SEC301_02", "http://data.europa.eu/4rx/ABB2018/SEC301_01_03"],
            "type_http://data.europa.eu/bud#Article": [2, 0, 1],
            "type_http://data.europa.eu/3rx#Article": [2, 0, 1],
            "type_http://data.europa.eu/bud#Item": [0, 1, 1],
            "type_http://data.europa.eu/3rx#Item": [0, 1, 1],
            "type_http://data.europa.eu/bud#Chapter": [0, 1, 0],
            "type_http://data.europa.eu/3rx#Chapter": [0, 1, 0]
            })

        result = direct_type_generator(df, ["uri1","uri2"], result_type = "count", bundled_mode=True, endpoint=EUOpenData)

        pd.testing.assert_frame_equal(result, expected_result_df, check_like = True)


    def test9_eurostat_boolean_multipleinputs(self):

        df = pd.DataFrame({
            "label": ["Element 1", "Element 2", "Element 3"], 
            "uri1": ["http://data.europa.eu/4rx/ABB2018/SEC301_01_01", "http://data.europa.eu/4rx/ABB2018/SEC301_01_02_01", "http://data.europa.eu/4rx/ABB2018/SEC301_02_77_01"],
            "uri2": ["http://data.europa.eu/4rx/ABB2018/SEC301_03_02", "http://data.europa.eu/4rx/ABB2018/SEC301_02", "http://data.europa.eu/4rx/ABB2018/SEC301_01_03"]
            })

        expected_result_df = pd.DataFrame({
            "label": ["Element 1", "Element 2", "Element 3"], 
            "uri1": ["http://data.europa.eu/4rx/ABB2018/SEC301_01_01", "http://data.europa.eu/4rx/ABB2018/SEC301_01_02_01", "http://data.europa.eu/4rx/ABB2018/SEC301_02_77_01"],
            "uri2": ["http://data.europa.eu/4rx/ABB2018/SEC301_03_02", "http://data.europa.eu/4rx/ABB2018/SEC301_02", "http://data.europa.eu/4rx/ABB2018/SEC301_01_03"],
            "type_http://data.europa.eu/bud#Article": [True, False, True],
            "type_http://data.europa.eu/3rx#Article": [True, False, True],
            "type_http://data.europa.eu/bud#Item": [False, True, True],
            "type_http://data.europa.eu/3rx#Item": [False, True, True],
            "type_http://data.europa.eu/bud#Chapter": [False, True, False],
            "type_http://data.europa.eu/3rx#Chapter": [False, True, False]
            })

        result = direct_type_generator(df, ["uri1","uri2"], result_type = "boolean", bundled_mode=True, endpoint=EUOpenData)

        pd.testing.assert_frame_equal(result, expected_result_df, check_like = True)

    def test10_hierarchy(self):

        df = pd.DataFrame({
            "label": ["Explorair", "Rhein-Flugzeugbau", "Buxton Watermill"], 
            "uri": ["http://dbpedia.org/resource/Explorair", "http://dbpedia.org/resource/Rhein-Flugzeugbau", "http://dbpedia.org/resource/Buxton_Watermill"]
            })

        expected_nodes = ["http://dbpedia.org/ontology/Agent", "http://dbpedia.org/ontology/Company", 
                          "http://dbpedia.org/ontology/Location", "http://dbpedia.org/ontology/Organisation", 
                          "http://dbpedia.org/ontology/Place", "http://schema.org/Organization",
                          "http://schema.org/Place", "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Agent",
                          "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#SocialPerson", "http://www.w3.org/2002/07/owl#Thing",
                          "http://www.w3.org/2003/01/geo/wgs84_pos#SpatialThing", "http://www.wikidata.org/entity/Q24229398",
                          "http://www.wikidata.org/entity/Q43229", 'http://umbel.org/umbel/rc/Agent-Generic',
                          'http://purl.org/goodrelations/v1#BusinessEntity',
                          'http://umbel.org/umbel/rc/Business','http://umbel.org/umbel/rc/Organization',
                          'http://www.openlinksw.com/virtpivot/icons/Business','http://www.openlinksw.com/virtpivot/icons/Organization',
                          'http://www.w3.org/2002/07/owl#Thing','http://xmlns.com/foaf/0.1/Organization',
                          'http://umbel.org/umbel/rc/Place','http://www.wikidata.org/entity/Q874405']
        expected_edges = [('http://dbpedia.org/ontology/Company','http://purl.org/goodrelations/v1#BusinessEntity'),
                          ('http://dbpedia.org/ontology/Company','http://dbpedia.org/ontology/Organisation'),
                          ('http://dbpedia.org/ontology/Company', 'http://umbel.org/umbel/rc/Business'),
                          ('http://purl.org/goodrelations/v1#BusinessEntity','http://xmlns.com/foaf/0.1/Organization'),
                          ('http://purl.org/goodrelations/v1#BusinessEntity','http://www.openlinksw.com/virtpivot/icons/Business'),
                          ('http://dbpedia.org/ontology/Organisation','http://dbpedia.org/ontology/Agent'),
                          ('http://dbpedia.org/ontology/Organisation','http://umbel.org/umbel/rc/Organization'),
                          ('http://dbpedia.org/ontology/Place',"http://www.w3.org/2002/07/owl#Thing"),
                          ('http://dbpedia.org/ontology/Place','http://umbel.org/umbel/rc/Place'),
                          ('http://www.wikidata.org/entity/Q43229','http://www.wikidata.org/entity/Q874405'),
                          ('http://dbpedia.org/ontology/Agent', 'http://www.w3.org/2002/07/owl#Thing'),
                          ('http://dbpedia.org/ontology/Agent','http://umbel.org/umbel/rc/Agent-Generic'),
                          ('http://xmlns.com/foaf/0.1/Organization', 'http://www.openlinksw.com/virtpivot/icons/Organization')]
        expectedGraph = nx.DiGraph()
        expectedGraph.add_nodes_from(expected_nodes)
        expectedGraph.add_edges_from(expected_edges)

        result = direct_type_generator(df, ["uri"], result_type = "boolean", bundled_mode=False, hierarchy = True)
        outputhierarchyGraph = result.attrs['hierarchy']

        assert nx.is_isomorphic(expectedGraph, outputhierarchyGraph)



class TestSpecificRelationGenerator:

    def test1_dbpedia_direct_relation_one_col(self):
        input = pd.DataFrame({
            'a':[0, 1], 
            'new_link': ['http://dbpedia.org/resource/Stuttgart',
                         'http://dbpedia.org/resource/Tübingen']
        })

        path_expected = "test/data/generator/srg_1_expected.csv"
        expected = pd.read_csv(path_expected)

        output = specific_relation_generator(input, 'new_link')

        expected = expected.apply(lambda x: x.astype('object'))
        output = output.apply(lambda x: x.astype('object'))

        pd.testing.assert_frame_equal(output, expected, check_like = True)

    def test2_dbpedia_direct_relation_two_cols(self):

        input = pd.DataFrame({
            'a':['http://dbpedia.org/resource/Boris_Palmer', 'http://dbpedia.org/resource/Patrick_Schmollinger'], 
            'b': ['http://dbpedia.org/resource/13', 'http://dbpedia.org/resource/753']
        })

        path_expected = "test/data/generator/srg_2_expected.csv"
        expected = pd.read_csv(path_expected)

        output = specific_relation_generator(input, ['a', 'b'])

        expected = expected.apply(lambda x: x.astype('object'))
        output = output.apply(lambda x: x.astype('object'))

        pd.testing.assert_frame_equal(output, expected, check_like = True)

    def test3_dbpedia_hierarchy_relation_depth_1(self):
        
        input = pd.DataFrame({
            'a': ['http://dbpedia.org/resource/1913', 'http://dbpedia.org/resource/2020']
        })

        expected_nodes = ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:2020',
                          'http://dbpedia.org/resource/Category:1910s', 'http://dbpedia.org/resource/Category:Years',
                          'http://dbpedia.org/resource/Category:2020s', 'http://dbpedia.org/resource/Category:Years_in_the_future']
        expected_edges = [('http://dbpedia.org/resource/Category:1913','http://dbpedia.org/resource/Category:1910s'),
                          ('http://dbpedia.org/resource/Category:1913','http://dbpedia.org/resource/Category:Years'),
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:2020s'),
                          ('http://dbpedia.org/resource/Category:2020','http://dbpedia.org/resource/Category:Years'),
                          ('http://dbpedia.org/resource/Category:2020','http://dbpedia.org/resource/Category:Years_in_the_future')]
        expectedGraph = nx.DiGraph()
        expectedGraph.add_nodes_from(expected_nodes)
        expectedGraph.add_edges_from(expected_edges)

        output = specific_relation_generator(input, 'a', 
                 hierarchy_relation='http://www.w3.org/2004/02/skos/core#broader', max_hierarchy_depth=1)

        outputhierarchyGraph = output.attrs['hierarchy']

        assert nx.is_isomorphic(expectedGraph, outputhierarchyGraph)

    def test4_dbpedia_nonexisting_uris(self):
        
        input = pd.DataFrame({
            'a': ['http://dbpedia.org/fake/Angela_Merkel', 'http://dbpedia.org/fake/Donald_Trump']
        })

        expected = pd.DataFrame({
            'a': ['http://dbpedia.org/fake/Angela_Merkel', 'http://dbpedia.org/fake/Donald_Trump']
        })

        output = specific_relation_generator(input, 'a', 
        hierarchy_relation='http://www.w3.org/2004/02/skos/core#broader', max_hierarchy_depth=2)

        pd.testing.assert_frame_equal(output, expected, check_like = True)

    def test5_dbpedia_duplicate_uris(self):
        
        input = pd.DataFrame({
            'a': ['http://dbpedia.org/resource/1913', 
                  'http://dbpedia.org/resource/1913',
                  'http://dbpedia.org/fake/1913']
        })

        expected = pd.DataFrame({
            'a': ['http://dbpedia.org/resource/1913', 
                  'http://dbpedia.org/resource/1913',
                  'http://dbpedia.org/fake/1913'],
            'a_in_boolean_http://dbpedia.org/resource/Category:1913': [True, True, np.nan]
        })

        output = specific_relation_generator(input, 'a')

        expected = expected.apply(lambda x: x.astype('object'))
        output = output.apply(lambda x: x.astype('object'))

        pd.testing.assert_frame_equal(output, expected, check_like = True)


    def test6_dbpedia_hierarchy_relation_two_cols(self):

        input = pd.DataFrame({
            'a':['http://dbpedia.org/resource/1913'], 
            'b': ['http://dbpedia.org/resource/2020']
        })

        expected_nodes = ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:2020',
                          'http://dbpedia.org/resource/Category:1910s', 'http://dbpedia.org/resource/Category:Years',
                          'http://dbpedia.org/resource/Category:2020s', 'http://dbpedia.org/resource/Category:Years_in_the_future']
        expected_edges = [('http://dbpedia.org/resource/Category:1913','http://dbpedia.org/resource/Category:1910s'),
                          ('http://dbpedia.org/resource/Category:1913','http://dbpedia.org/resource/Category:Years'),
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:2020s'),
                          ('http://dbpedia.org/resource/Category:2020','http://dbpedia.org/resource/Category:Years'),
                          ('http://dbpedia.org/resource/Category:2020','http://dbpedia.org/resource/Category:Years_in_the_future')]
        expectedGraph = nx.DiGraph()
        expectedGraph.add_nodes_from(expected_nodes)
        expectedGraph.add_edges_from(expected_edges)

        output = specific_relation_generator(input, ['a', 'b'], hierarchy_relation='http://www.w3.org/2004/02/skos/core#broader', max_hierarchy_depth=1)
        outputhierarchyGraph = output.attrs['hierarchy']

        assert nx.is_isomorphic(expectedGraph, outputhierarchyGraph)

    def test7_dbpedia_other_direct_relation(self):
        input = pd.DataFrame({
            'a':[0, 1], 
            'new_link': ['http://dbpedia.org/resource/Stuttgart',
                         'http://dbpedia.org/resource/Tübingen']
        })

        path_expected = "test/data/generator/srg_7_expected.csv"
        expected = pd.read_csv(path_expected)

        output = specific_relation_generator(input, 'new_link', 
            direct_relation='https://www.w3.org/2000/01/rdf-schema#seeAlso')


        expected = expected.apply(lambda x: x.astype('object'))
        output = output.apply(lambda x: x.astype('object'))

        pd.testing.assert_frame_equal(output, expected, check_like = True)

    def test8_one_nan(self):
        input = pd.DataFrame({
            'a':[0, 1], 
            'new_link': [np.nan,
                         'http://dbpedia.org/resource/Tübingen']
        })

        path_expected = "test/data/generator/srg_8_expected.csv"
        expected = pd.read_csv(path_expected)

        output = specific_relation_generator(input, 'new_link', 
            direct_relation='https://www.w3.org/2000/01/rdf-schema#seeAlso')


        expected = expected.apply(lambda x: x.astype('object'))
        output = output.apply(lambda x: x.astype('object'))

        pd.testing.assert_frame_equal(output, expected, check_like = True)

    def test9_all_nan(self):
        input = pd.DataFrame({
            'a':[0, 1], 
            'new_link': [np.nan,np.nan]
        })

        expected = input.copy()

        output = specific_relation_generator(input, 'new_link', 
            direct_relation='https://www.w3.org/2000/01/rdf-schema#seeAlso')

        expected = expected.apply(lambda x: x.astype('object'))
        output = output.apply(lambda x: x.astype('object'))

        pd.testing.assert_frame_equal(output, expected, check_like = True)


class TestUnqualifiedRelationGenerator:

    def test1_out_boolean_bundled(self):

        df = pd.DataFrame({
            "label": ["Hamburg", "Bremen"],
            "uri": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Bremen"]
            })
                                            
        path_expected = "test/data/generator/unqr_1_expected.csv"
        expected = pd.read_csv(path_expected)    
                                            
        result = unqualified_relation_generator(df, columns="uri")

        pd.testing.assert_frame_equal(result, expected, check_like = True)  
                                                    
    def test2_out_count(self):
                                            
        df = pd.DataFrame({
           "label": ["Hamburg", "Bremen"],
            "uri": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Bremen"]
            })
                                            
        path_expected = "test/data/generator/unqr_2_expected.csv"
        expected = pd.read_csv(path_expected)  
        
        result = unqualified_relation_generator(df, columns="uri", direction="Out", result_type="count")
                                            
        pd.testing.assert_frame_equal(result, expected, check_like = True)  


    def test3_in_filter_count(self):

        df = pd.DataFrame({
            "label": ["Hamburg", "Bremen"],
            "uri": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Bremen"]
            })
        
        expected = pd.DataFrame({
            "label": ["Hamburg", "Bremen"], 
            "uri": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Bremen"],
            "Link_In_count_http://dbpedia.org/ontology/birthPlace": [1326, 302],
            "Link_In_count_http://dbpedia.org/ontology/deathPlace": [768, 157],
            "Link_In_count_http://dbpedia.org/ontology/wikiPageWikiLink": [7447, 0]
        })
        
        result = unqualified_relation_generator(df, columns="uri", direction="In", regex_filter=["ontology"], result_type="count")
           
        pd.testing.assert_frame_equal(result, expected, check_like = True)        
        
    def test4_out_boolean_uri_data_model(self):

        df = pd.DataFrame({
            "label": ["Hamburg", "Bremen"],
            "uri": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Bremen"]
            })
                                            
        path_expected = "test/data/generator/unqr_4_expected.csv"
        expected = pd.read_csv(path_expected)  
         
        result = unqualified_relation_generator(df, columns="uri", uri_data_model=True, direction="Out", regex_filter=["ontology"], result_type="boolean")
        
        pd.testing.assert_frame_equal(result, expected, check_like = True)
        
    def test5_missingvalue(self):
        
        df = pd.DataFrame({
           "label": ["Hamburg", "Bremen","abc"],
            "uri": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Bremen", "http://dbpedia.org/resource/abc"]
                })

        expected = pd.DataFrame({
                "label": ["Hamburg", "Bremen", "abc"], 
                "uri": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Bremen","http://dbpedia.org/resource/abc"],
                "Link_In_count_http://dbpedia.org/ontology/birthPlace": [1326.0, 302.0, 0.0],
                "Link_In_count_http://dbpedia.org/ontology/deathPlace": [768.0, 157.0, 0.0],
                "Link_In_count_http://dbpedia.org/ontology/wikiPageWikiLink": [7180.0, 0.0, 0.0],
                "Link_In_count_http://dbpedia.org/property/birthPlace": [88, 27, 0],
                "Link_In_count_http://dbpedia.org/property/deathPlace": [113, 27, 0],
                "Link_In_count_http://www.w3.org/2000/01/rdf-schema#seeAlso": [12, 0, 0]
        })

        result = unqualified_relation_generator(df, columns="uri", direction="In", result_type="count")

        pd.testing.assert_frame_equal(result, expected, check_like = True)
        
    def test6_out_relative(self):
        
        df = pd.DataFrame({
           "label": ["Hamburg", "Bremen"],
            "uri": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Bremen"]
            })
        
        path_expected = "test/data/generator/unqr_6_expected.csv"
        expected = pd.read_csv(path_expected) 
        
        result = unqualified_relation_generator(df, columns="uri", direction="Out", result_type="relative")
                                            
        pd.testing.assert_frame_equal(result, expected, check_like = True) 
    
    def test7_in_tfidf(self):
        
        df = pd.DataFrame({
           "label": ["Hamburg", "Bremen"],
            "uri": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Bremen"]
            })
        
        path_expected = "test/data/generator/unqr_7_expected.csv"
        expected = pd.read_csv(path_expected) 
        
        result = unqualified_relation_generator(df, columns="uri", direction="In", result_type="tfidf")
                                            
        pd.testing.assert_frame_equal(result, expected, check_like = True)
        
        
class TestQualifiedRelationGenerator:
    
    def test1_in_boolean_types_regex_filter(self):
                                            
        df = pd.DataFrame({
           "label": ["Hamburg", "Bremen"],
            "uri": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Bremen"]
            }) 
        
        path_expected = "test/data/generator/qr_1_expected.csv"
        expected = pd.read_csv(path_expected)  
                                                      
        result = qualified_relation_generator(df, columns="uri", direction="In", types_regex_filter=["place"], result_type="boolean")
                                                  
        pd.testing.assert_frame_equal(result, expected, check_like = True)
                                                  

    def test2_in_count_properties_regex_filter(self):

        df = pd.DataFrame({
            "label": ["Hamburg", "Bremen"],
            "uri": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Bremen"]
            }) 
        
        path_expected = "test/data/generator/qr_2_expected.csv"
        expected = pd.read_csv(path_expected) 
        
        result = qualified_relation_generator(df, columns="uri", direction="In", properties_regex_filter=["place"], result_type="count")
                                              
        pd.testing.assert_frame_equal(result, expected, check_like = True)
               
    def test3_out_count_uri_data_model_filter(self):

        df = pd.DataFrame({
            "label": ["Hamburg", "Bremen"],
            "uri": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Bremen"]
            }) 
        
        path_expected = "test/data/generator/qr_3_expected.csv"
        expected = pd.read_csv(path_expected) 
        
        result = qualified_relation_generator(df, columns="uri", uri_data_model=True, direction="Out", types_regex_filter=['City'], result_type="count", hierarchy = False)
        
        pd.testing.assert_frame_equal(result, expected, check_like = True)
        
    def test4_missingvalue(self):
        
        df = pd.DataFrame({
           "label": ["Hamburg", "Bremen","abc"],
            "uri": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Bremen", "http://dbpedia.org/resource/abc"]
                })
        
        path_expected = "test/data/generator/qr_4_expected.csv"
        expected = pd.read_csv(path_expected) 
        
        result = qualified_relation_generator(df, columns="uri", direction="In", properties_regex_filter=["place"], result_type="count")
        
        pd.testing.assert_frame_equal(result, expected, check_like = True)  

    def test5_in_relative_properties_regex_filter(self):
        
        df = pd.DataFrame({
            "label": ["Hamburg", "Bremen"],
            "uri": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Bremen"]
            }) 
        
        path_expected = "test/data/generator/qr_5_expected.csv"
        expected = pd.read_csv(path_expected) 
        
        result = qualified_relation_generator(df, columns="uri", direction="In", properties_regex_filter=["place"], result_type="relative")
                                              
        pd.testing.assert_frame_equal(result, expected, check_like = True)
        
    def test6_out_tfidf_types_regex_filter(self):
        
        df = pd.DataFrame({
            "label": ["Hamburg", "Bremen"],
            "uri": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Bremen"]
            }) 
        
        path_expected = "test/data/generator/qr_6_expected.csv"
        expected = pd.read_csv(path_expected) 
        
        result = qualified_relation_generator(df, columns="uri", direction="Out", types_regex_filter=['City'], result_type="tfidf")
        
        pd.testing.assert_frame_equal(result, expected, check_like = True)
        
    def test7_in_boolean_hierarchy(self):
                                            
        df = pd.DataFrame({
           "label": ["Hamburg", "Bremen"],
            "uri": ["http://dbpedia.org/resource/Hamburg", "http://dbpedia.org/resource/Bremen"]
            }) 
        
        expected_nodes = ['http://dbpedia.org/class/yago/DisplacedPerson110017890', 'http://dbpedia.org/class/yago/Refugee110516016', 
                          'http://dbpedia.org/class/yago/Marketplace103722288', 'http://dbpedia.org/class/yago/MercantileEstablishment103748162',
                          'http://dbpedia.org/class/yago/Workplace104602044', 'http://dbpedia.org/class/yago/GeographicPoint108578706', 
                          'http://dbpedia.org/class/yago/WikicatDisplacedPersonsCampsInTheAftermathOfWorldWarII', 
                          'http://dbpedia.org/class/yago/Camp102944826', 'http://dbpedia.org/class/yago/MilitaryQuarters103763727', 
                          'http://dbpedia.org/class/yago/Point108620061', 'http://dbpedia.org/class/yago/PlaceOfBusiness103953020', 
                          'http://dbpedia.org/class/yago/Exile110071332', 'http://dbpedia.org/class/yago/Absentee109757653', 
                          'http://dbpedia.org/class/yago/LivingQuarters103679384', 'http://dbpedia.org/class/yago/Establishment103297735', 
                          'http://dbpedia.org/class/yago/Location100027167', 'http://dbpedia.org/class/yago/Traveler109629752', 
                          'http://dbpedia.org/class/yago/Structure104341686', 'http://dbpedia.org/class/yago/Housing103546340', 
                          'http://dbpedia.org/class/yago/Object100002684', 'http://dbpedia.org/class/yago/YagoGeoEntity', 
                          'http://dbpedia.org/class/yago/YagoLegalActorGeo', 'http://dbpedia.org/class/yago/PhysicalEntity100001930', 
                          'http://dbpedia.org/class/yago/Artifact100021939', 'http://dbpedia.org/class/yago/Person100007846', 
                          'http://dbpedia.org/class/yago/YagoPermanentlyLocatedEntity', 'http://dbpedia.org/class/yago/Whole100003553', 
                          'http://dbpedia.org/class/yago/CausalAgent100007347', 'http://dbpedia.org/class/yago/Organism100004475', 
                          'http://dbpedia.org/class/yago/YagoLegalActor', 'http://dbpedia.org/class/yago/LivingThing100004258']
        expected_edges = [('http://dbpedia.org/class/yago/DisplacedPerson110017890', 'http://dbpedia.org/class/yago/Refugee110516016'), 
                          ('http://dbpedia.org/class/yago/Refugee110516016', 'http://dbpedia.org/class/yago/Exile110071332'), 
                          ('http://dbpedia.org/class/yago/Marketplace103722288', 'http://dbpedia.org/class/yago/MercantileEstablishment103748162'), 
                          ('http://dbpedia.org/class/yago/MercantileEstablishment103748162', 'http://dbpedia.org/class/yago/PlaceOfBusiness103953020'), 
                          ('http://dbpedia.org/class/yago/Workplace104602044', 'http://dbpedia.org/class/yago/GeographicPoint108578706'), 
                          ('http://dbpedia.org/class/yago/GeographicPoint108578706', 'http://dbpedia.org/class/yago/Point108620061'), 
                          ('http://dbpedia.org/class/yago/WikicatDisplacedPersonsCampsInTheAftermathOfWorldWarII', 'http://dbpedia.org/class/yago/Camp102944826'), 
                          ('http://dbpedia.org/class/yago/Camp102944826', 'http://dbpedia.org/class/yago/MilitaryQuarters103763727'), 
                          ('http://dbpedia.org/class/yago/MilitaryQuarters103763727', 'http://dbpedia.org/class/yago/LivingQuarters103679384'), 
                          ('http://dbpedia.org/class/yago/Point108620061', 'http://dbpedia.org/class/yago/Location100027167'), 
                          ('http://dbpedia.org/class/yago/PlaceOfBusiness103953020', 'http://dbpedia.org/class/yago/Establishment103297735'), 
                          ('http://dbpedia.org/class/yago/Exile110071332', 'http://dbpedia.org/class/yago/Absentee109757653'), 
                          ('http://dbpedia.org/class/yago/Absentee109757653', 'http://dbpedia.org/class/yago/Traveler109629752'), 
                          ('http://dbpedia.org/class/yago/LivingQuarters103679384', 'http://dbpedia.org/class/yago/Housing103546340'), 
                          ('http://dbpedia.org/class/yago/Establishment103297735', 'http://dbpedia.org/class/yago/Structure104341686'), 
                          ('http://dbpedia.org/class/yago/Location100027167', 'http://dbpedia.org/class/yago/Object100002684'), 
                          ('http://dbpedia.org/class/yago/Location100027167', 'http://dbpedia.org/class/yago/YagoGeoEntity'), 
                          ('http://dbpedia.org/class/yago/Location100027167', 'http://dbpedia.org/class/yago/YagoLegalActorGeo'), 
                          ('http://dbpedia.org/class/yago/Traveler109629752', 'http://dbpedia.org/class/yago/Person100007846'), 
                          ('http://dbpedia.org/class/yago/Structure104341686', 'http://dbpedia.org/class/yago/Artifact100021939'), 
                          ('http://dbpedia.org/class/yago/Structure104341686', 'http://dbpedia.org/class/yago/YagoGeoEntity'), 
                          ('http://dbpedia.org/class/yago/Housing103546340', 'http://dbpedia.org/class/yago/Structure104341686'), 
                          ('http://dbpedia.org/class/yago/Object100002684', 'http://dbpedia.org/class/yago/PhysicalEntity100001930'), 
                          ('http://dbpedia.org/class/yago/YagoGeoEntity', 'http://dbpedia.org/class/yago/YagoPermanentlyLocatedEntity'), 
                          ('http://dbpedia.org/class/yago/Artifact100021939', 'http://dbpedia.org/class/yago/Whole100003553'), 
                          ('http://dbpedia.org/class/yago/Person100007846', 'http://dbpedia.org/class/yago/CausalAgent100007347'), 
                          ('http://dbpedia.org/class/yago/Person100007846', 'http://dbpedia.org/class/yago/Organism100004475'), 
                          ('http://dbpedia.org/class/yago/Person100007846', 'http://dbpedia.org/class/yago/YagoLegalActor'), 
                          ('http://dbpedia.org/class/yago/Whole100003553', 'http://dbpedia.org/class/yago/Object100002684'), 
                          ('http://dbpedia.org/class/yago/CausalAgent100007347', 'http://dbpedia.org/class/yago/PhysicalEntity100001930'), 
                          ('http://dbpedia.org/class/yago/Organism100004475', 'http://dbpedia.org/class/yago/LivingThing100004258'), 
                          ('http://dbpedia.org/class/yago/YagoLegalActor', 'http://dbpedia.org/class/yago/YagoLegalActorGeo'), 
                          ('http://dbpedia.org/class/yago/LivingThing100004258', 'http://dbpedia.org/class/yago/Whole100003553')]
        expectedGraph = nx.DiGraph()
        expectedGraph.add_nodes_from(expected_nodes)
        expectedGraph.add_edges_from(expected_edges)
                                                      
        result = qualified_relation_generator(df, columns="uri", direction="In", types_regex_filter=["place"], result_type="boolean", hierarchy=True)
        outputhierarchyGraph = result.attrs['hierarchy']
         
        assert nx.is_isomorphic(expectedGraph, outputhierarchyGraph)
                                                  
        
    
class TestCustomSparqlGenerator:

    def test1_dbpedia_one_result(self):

        df = pd.DataFrame({
            "label": ["Baden-Württemberg", "Brandenburg", "Saarland"], 
            "uri": ["http://dbpedia.org/resource/Baden-Württemberg", "http://dbpedia.org/resource/Brandenburg", "http://dbpedia.org/resource/Saarland"]
            })

        expected_result_df = pd.DataFrame({
                    "label": ["Baden-Württemberg", "Brandenburg", "Saarland"], 
                    "uri": ["http://dbpedia.org/resource/Baden-Württemberg", "http://dbpedia.org/resource/Brandenburg", "http://dbpedia.org/resource/Saarland"],
                    "population": [10777514, 2449600, 1039000]
        })

        sparql_query = "select ?population where {*uri* <http://dbpedia.org/ontology/populationTotal> ?population .}"

        result = custom_sparql_generator(df, ["uri"], endpoint = DBpedia, query = sparql_query)

        pd.testing.assert_frame_equal(result, expected_result_df)

    def test2_dbpedia_multiple_results(self):
        
        df = pd.DataFrame({
            "label": ["Baden-Württemberg", "Brandenburg", "Saarland"], 
            "uri": ["http://dbpedia.org/resource/Baden-Württemberg", "http://dbpedia.org/resource/Brandenburg", "http://dbpedia.org/resource/Saarland"]
            })

        expected_result_df = pd.DataFrame({
                    "label": ["Baden-Württemberg", "Brandenburg", "Saarland"], 
                    "uri": ["http://dbpedia.org/resource/Baden-Württemberg", "http://dbpedia.org/resource/Brandenburg", "http://dbpedia.org/resource/Saarland"],
                    "capital": ["Stuttgart", "Potsdam", "Saarbrücken"],
                    "populationCap": [623738, 161468, 180515]
        })

        sparql_query = "select ?capital ?populationCap where {*uri* <http://dbpedia.org/ontology/capital> ?capitalLink . \
                        ?capitalLink rdfs:label ?capital . \
                        ?capitalLink <http://dbpedia.org/ontology/populationTotal> ?populationCap .}"

        result = custom_sparql_generator(df, ["uri"], endpoint = DBpedia, query = sparql_query)

        pd.testing.assert_frame_equal(result, expected_result_df)

        
class TestDataPropertiesGenerator:
    
    def test1_dbpedia(self):
        df = pd.DataFrame({
            "label": ["Eratosthenes","Pytheas"], 
            "uri": ["http://dbpedia.org/resource/Eratosthenes","http://dbpedia.org/resource/Pytheas"]
            })

        expected_result_columns = ['label', 'uri', 'uri_data_http://dbpedia.org/ontology/abstract',
                                   'uri_data_http://dbpedia.org/ontology/birthDate',
                                   'uri_data_http://dbpedia.org/ontology/birthYear',
                                   'uri_data_http://dbpedia.org/ontology/deathDate',
                                   'uri_data_http://dbpedia.org/ontology/deathYear',
                                   'uri_data_http://dbpedia.org/ontology/wikiPageID',
                                   'uri_data_http://dbpedia.org/ontology/wikiPageRevisionID',
                                   'uri_data_http://dbpedia.org/property/alt',
                                   'uri_data_http://dbpedia.org/property/birthDate',
                                   'uri_data_http://dbpedia.org/property/caption',
                                   'uri_data_http://dbpedia.org/property/citizenship',
                                   'uri_data_http://dbpedia.org/property/deathDate',
                                   'uri_data_http://dbpedia.org/property/ethnicity',
                                   'uri_data_http://dbpedia.org/property/fields',
                                   'uri_data_http://dbpedia.org/property/imageSize',
                                   'uri_data_http://dbpedia.org/property/influenced',
                                   'uri_data_http://purl.org/dc/terms/description',
                                   'uri_data_http://www.w3.org/2000/01/rdf-schema#comment',
                                   'uri_data_http://www.w3.org/2000/01/rdf-schema#label',
                                   'uri_data_http://xmlns.com/foaf/0.1/gender',
                                   'uri_data_http://xmlns.com/foaf/0.1/name']

        result = list(data_properties_generator(df, "uri").columns)
        
        assert result == expected_result_columns
    
    def test2_dbpedia_string(self):
        df = pd.DataFrame({
            "label": ["Eratosthenes","Pytheas"], 
            "uri": ["http://dbpedia.org/resource/Eratosthenes","http://dbpedia.org/resource/Pytheas"]
            })

        expected_result_columns = ['label', 'uri', 'uri_data_http://dbpedia.org/ontology/birthDate',
                                   'uri_data_http://dbpedia.org/ontology/birthYear',
                                   'uri_data_http://dbpedia.org/ontology/deathDate',
                                   'uri_data_http://dbpedia.org/ontology/deathYear',
                                   'uri_data_http://dbpedia.org/ontology/wikiPageID',
                                   'uri_data_http://dbpedia.org/ontology/wikiPageRevisionID',
                                   'uri_data_http://dbpedia.org/property/alt',
                                   'uri_data_http://dbpedia.org/property/birthDate',
                                   'uri_data_http://dbpedia.org/property/caption',
                                   'uri_data_http://dbpedia.org/property/citizenship',
                                   'uri_data_http://dbpedia.org/property/deathDate',
                                   'uri_data_http://dbpedia.org/property/ethnicity',
                                   'uri_data_http://dbpedia.org/property/fields',
                                   'uri_data_http://dbpedia.org/property/imageSize',
                                   'uri_data_http://dbpedia.org/property/influenced']

        result = list(data_properties_generator(df, "uri", type_filter="- xsd:string").columns)
        
        assert result == expected_result_columns
    
    def test3_dbpedia_regex(self):
        df = pd.DataFrame({
            "label": ["Eratosthenes","Pytheas"], 
            "uri": ["http://dbpedia.org/resource/Eratosthenes","http://dbpedia.org/resource/Pytheas"]
            })
        
        expected_result_columns = ['label', 'uri',
                                   'uri_data_http://dbpedia.org/property/alt',
                                   'uri_data_http://dbpedia.org/property/birthDate',
                                   'uri_data_http://dbpedia.org/property/caption',
                                   'uri_data_http://dbpedia.org/property/citizenship',
                                   'uri_data_http://dbpedia.org/property/deathDate',
                                   'uri_data_http://dbpedia.org/property/ethnicity',
                                   'uri_data_http://dbpedia.org/property/fields',
                                   'uri_data_http://dbpedia.org/property/imageSize',
                                   'uri_data_http://dbpedia.org/property/influenced']
        
        result = list(data_properties_generator(df, "uri", regex_filter=".*property.*").columns)
        
        assert result == expected_result_columns
    
    def test4_dbpedia_date_regex(self):
        df = pd.DataFrame({
            "label": ["Eratosthenes","Pytheas"], 
            "uri": ["http://dbpedia.org/resource/Eratosthenes","http://dbpedia.org/resource/Pytheas"]
            })
        
        expected_result_columns = ['label', 'uri',
                                   'uri_data_http://dbpedia.org/property/alt',
                                   'uri_data_http://dbpedia.org/property/birthDate',
                                   'uri_data_http://dbpedia.org/property/caption',
                                   'uri_data_http://dbpedia.org/property/citizenship',
                                   'uri_data_http://dbpedia.org/property/deathDate',
                                   'uri_data_http://dbpedia.org/property/ethnicity',
                                   'uri_data_http://dbpedia.org/property/fields',
                                   'uri_data_http://dbpedia.org/property/imageSize',
                                   'uri_data_http://dbpedia.org/property/influenced']
        
        result = list(data_properties_generator(df, "uri", type_filter="xsd:date",regex_filter=".*property.*").columns)
        
        assert result == expected_result_columns
