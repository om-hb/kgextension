import pandas as pd
import numpy as np
import networkx as nx
import pytest

from kgextension.generator_helper import hierarchy_graph_generator

class TestHierarchyGenerator:

    def test1_default_behaviour(self):

        input_df = pd.DataFrame({
            'value': ['http://dbpedia.org/resource/Explorair'] * 3 + ['http://dbpedia.org/resource/Buxton_Watermill'] * 2,
            'types': ['http://www.w3.org/2002/07/owl#Thing',
                      'http://dbpedia.org/ontology/Company',
                      'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Agent',
                      'http://www.w3.org/2002/07/owl#Thing',
                      'http://dbpedia.org/ontology/Place']
        })

        expected_DG = nx.DiGraph()
        expected_nodes = ['http://dbpedia.org/ontology/Company', 'http://purl.org/goodrelations/v1#BusinessEntity', 
                          'http://dbpedia.org/ontology/Organisation', 'http://umbel.org/umbel/rc/Business', 
                          'http://dbpedia.org/ontology/Place', 'http://www.w3.org/2002/07/owl#Thing', 
                          'http://umbel.org/umbel/rc/Place', 'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Agent', 
                          'http://xmlns.com/foaf/0.1/Organization', 'http://www.openlinksw.com/virtpivot/icons/Business', 
                          'http://dbpedia.org/ontology/Agent', 'http://umbel.org/umbel/rc/Organization', 
                          'http://www.openlinksw.com/virtpivot/icons/Organization', 'http://umbel.org/umbel/rc/Agent-Generic']
        expected_edges = [('http://dbpedia.org/ontology/Company', 'http://purl.org/goodrelations/v1#BusinessEntity'), 
                          ('http://dbpedia.org/ontology/Company', 'http://dbpedia.org/ontology/Organisation'),
                          ('http://dbpedia.org/ontology/Company', 'http://umbel.org/umbel/rc/Business'), 
                          ('http://purl.org/goodrelations/v1#BusinessEntity', 'http://xmlns.com/foaf/0.1/Organization'), 
                          ('http://purl.org/goodrelations/v1#BusinessEntity', 'http://www.openlinksw.com/virtpivot/icons/Business'), 
                          ('http://dbpedia.org/ontology/Organisation', 'http://dbpedia.org/ontology/Agent'), 
                          ('http://dbpedia.org/ontology/Organisation', 'http://umbel.org/umbel/rc/Organization'), 
                          ('http://dbpedia.org/ontology/Place', 'http://www.w3.org/2002/07/owl#Thing'), 
                          ('http://dbpedia.org/ontology/Place', 'http://umbel.org/umbel/rc/Place'), 
                          ('http://xmlns.com/foaf/0.1/Organization', 'http://www.openlinksw.com/virtpivot/icons/Organization'), 
                          ('http://dbpedia.org/ontology/Agent', 'http://www.w3.org/2002/07/owl#Thing'), 
                          ('http://dbpedia.org/ontology/Agent', 'http://umbel.org/umbel/rc/Agent-Generic')]
        expected_DG.add_nodes_from(expected_nodes)
        expected_DG.add_edges_from(expected_edges)

        output_DG = hierarchy_graph_generator(input_df['types'])

        assert nx.is_isomorphic(expected_DG, output_DG)

    def test2_subclass_with_max_depth(self):

        input_df = pd.DataFrame({
            'value': ['http://dbpedia.org/resource/Explorair'] * 3 + ['http://dbpedia.org/resource/Buxton_Watermill'] * 2,
            'types': ['http://www.w3.org/2002/07/owl#Thing',
                      'http://dbpedia.org/ontology/Company',
                      'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Agent',
                      'http://www.w3.org/2002/07/owl#Thing',
                      'http://dbpedia.org/ontology/Place']
        })

        expected_DG = nx.DiGraph()
        expected_nodes = ['http://dbpedia.org/ontology/Company', 'http://purl.org/goodrelations/v1#BusinessEntity', 
                          'http://dbpedia.org/ontology/Organisation', 'http://umbel.org/umbel/rc/Business', 
                          'http://dbpedia.org/ontology/Place', 'http://www.w3.org/2002/07/owl#Thing', 
                          'http://umbel.org/umbel/rc/Place', 'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Agent', 
                          'http://xmlns.com/foaf/0.1/Organization', 'http://www.openlinksw.com/virtpivot/icons/Business', 
                          'http://dbpedia.org/ontology/Agent', 'http://umbel.org/umbel/rc/Organization', 
                          'http://www.openlinksw.com/virtpivot/icons/Organization', 'http://umbel.org/umbel/rc/Agent-Generic']
        expected_edges = [('http://dbpedia.org/ontology/Company', 'http://purl.org/goodrelations/v1#BusinessEntity'), 
                          ('http://dbpedia.org/ontology/Company', 'http://dbpedia.org/ontology/Organisation'),
                          ('http://dbpedia.org/ontology/Company', 'http://umbel.org/umbel/rc/Business'), 
                          ('http://purl.org/goodrelations/v1#BusinessEntity', 'http://xmlns.com/foaf/0.1/Organization'), 
                          ('http://purl.org/goodrelations/v1#BusinessEntity', 'http://www.openlinksw.com/virtpivot/icons/Business'), 
                          ('http://dbpedia.org/ontology/Organisation', 'http://dbpedia.org/ontology/Agent'), 
                          ('http://dbpedia.org/ontology/Organisation', 'http://umbel.org/umbel/rc/Organization'), 
                          ('http://dbpedia.org/ontology/Place', 'http://www.w3.org/2002/07/owl#Thing'), 
                          ('http://dbpedia.org/ontology/Place', 'http://umbel.org/umbel/rc/Place'), 
                          ('http://xmlns.com/foaf/0.1/Organization', 'http://www.openlinksw.com/virtpivot/icons/Organization'), 
                          ('http://dbpedia.org/ontology/Agent', 'http://www.w3.org/2002/07/owl#Thing'), 
                          ('http://dbpedia.org/ontology/Agent', 'http://umbel.org/umbel/rc/Agent-Generic')]
        expected_DG.add_nodes_from(expected_nodes)
        expected_DG.add_edges_from(expected_edges)

        output_DG = hierarchy_graph_generator(input_df['types'], max_hierarchy_depth=2)

        assert nx.is_isomorphic(expected_DG, output_DG)


    def test3_skos_broader_max_1(self):

        input_df = pd.DataFrame({
            'category': ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:2020']
        })

        expected_DG = nx.DiGraph()
        expected_nodes = ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:1910s', 
                          'http://dbpedia.org/resource/Category:Years', 'http://dbpedia.org/resource/Category:2020', 
                          'http://dbpedia.org/resource/Category:2020s', 'http://dbpedia.org/resource/Category:Years_in_the_future']
        expected_edges = [('http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:1910s'), 
                          ('http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:Years'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:2020s'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:Years'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:Years_in_the_future')]
        expected_DG.add_nodes_from(expected_nodes)
        expected_DG.add_edges_from(expected_edges)


        output_DG = hierarchy_graph_generator(input_df['category'], hierarchy_relation="http://www.w3.org/2004/02/skos/core#broader",
                    max_hierarchy_depth=1)

        assert nx.is_isomorphic(expected_DG, output_DG)

    def test4_skos_broader_max_2(self):

        input_df = pd.DataFrame({
            'category': ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:2020']
        })

        expected_DG = nx.DiGraph()
        expected_nodes = ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:Years', 
                          'http://dbpedia.org/resource/Category:Chronology', 'http://dbpedia.org/resource/Category:Units_of_time', 
                          'http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:1910s', 
                          'http://dbpedia.org/resource/Category:20th_century', 'http://dbpedia.org/resource/Category:Decades', 
                          'http://dbpedia.org/resource/Category:Years_in_the_future', 'http://dbpedia.org/resource/Category:Time_periods_in_the_future', 
                          'http://dbpedia.org/resource/Category:2020s', 'http://dbpedia.org/resource/Category:21st_century', 
                          'http://dbpedia.org/resource/Category:Decades_in_the_future']
        expected_edges = [('http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:Years'), 
                          ('http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:1910s'), 
                          ('http://dbpedia.org/resource/Category:Years', 'http://dbpedia.org/resource/Category:Chronology'), 
                          ('http://dbpedia.org/resource/Category:Years', 'http://dbpedia.org/resource/Category:Units_of_time'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:Years'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:Years_in_the_future'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:2020s'), 
                          ('http://dbpedia.org/resource/Category:1910s', 'http://dbpedia.org/resource/Category:20th_century'), 
                          ('http://dbpedia.org/resource/Category:1910s', 'http://dbpedia.org/resource/Category:Decades'), 
                          ('http://dbpedia.org/resource/Category:Years_in_the_future', 'http://dbpedia.org/resource/Category:Years'), 
                          ('http://dbpedia.org/resource/Category:Years_in_the_future', 'http://dbpedia.org/resource/Category:Time_periods_in_the_future'), 
                          ('http://dbpedia.org/resource/Category:2020s', 'http://dbpedia.org/resource/Category:21st_century'), 
                          ('http://dbpedia.org/resource/Category:2020s', 'http://dbpedia.org/resource/Category:Decades'), 
                          ('http://dbpedia.org/resource/Category:2020s', 'http://dbpedia.org/resource/Category:Decades_in_the_future')]
        expected_DG.add_nodes_from(expected_nodes)
        expected_DG.add_edges_from(expected_edges)


        output_DG = hierarchy_graph_generator(input_df['category'], hierarchy_relation="http://www.w3.org/2004/02/skos/core#broader",
                    max_hierarchy_depth=2)

        assert nx.is_isomorphic(expected_DG, output_DG)

    def test5_skos_broader_hierarchy_none(self):

        input_df = pd.DataFrame({
            'category': ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:2020']
        })

        expected_DG = nx.DiGraph()
        expected_nodes = ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:1910s', 
                          'http://dbpedia.org/resource/Category:Years', 'http://dbpedia.org/resource/Category:2020', 
                          'http://dbpedia.org/resource/Category:2020s', 'http://dbpedia.org/resource/Category:Years_in_the_future']
        expected_edges = [('http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:1910s'), 
                          ('http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:Years'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:2020s'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:Years'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:Years_in_the_future')]
        expected_DG.add_nodes_from(expected_nodes)
        expected_DG.add_edges_from(expected_edges)


        output_DG = hierarchy_graph_generator(input_df['category'], hierarchy_relation="http://www.w3.org/2004/02/skos/core#broader",
                    max_hierarchy_depth=None)

        assert nx.is_isomorphic(expected_DG, output_DG)

    
    def test6_invalid_hierarchy_relation(self):

        input_df = pd.DataFrame({
            'category': ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:2020']
        })

        expected_DG = nx.DiGraph()
        expected_nodes = ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:2020']
        expected_DG.add_nodes_from(expected_nodes)


        output_DG = hierarchy_graph_generator(input_df['category'], hierarchy_relation="http://www.w3.org/2004/02/skos/ballaballa",
                    max_hierarchy_depth=None)

        assert nx.is_isomorphic(expected_DG, output_DG)

    def test7_default_nan(self):

        input_df = pd.DataFrame({
            'value': ['http://dbpedia.org/resource/Explorair'] * 3 + ['http://dbpedia.org/resource/Buxton_Watermill'] * 2,
            'types': ['http://www.w3.org/2002/07/owl#Thing',
                      np.nan,
                      'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Agent',
                      np.nan,
                      'http://dbpedia.org/ontology/Place']
        })

        expected_DG = nx.DiGraph()
        expected_nodes = ['http://dbpedia.org/ontology/Place', 
                          'http://www.w3.org/2002/07/owl#Thing', 
                          'http://umbel.org/umbel/rc/Place', 
                          'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Agent']
        expected_edges = [
            ('http://dbpedia.org/ontology/Place', 'http://www.w3.org/2002/07/owl#Thing'), 
            ('http://dbpedia.org/ontology/Place', 'http://umbel.org/umbel/rc/Place')]
        expected_DG.add_nodes_from(expected_nodes)
        expected_DG.add_edges_from(expected_edges)

        output_DG = hierarchy_graph_generator(input_df['types'])

        assert nx.is_isomorphic(expected_DG, output_DG)

    def test8_skos_broader_nan(self):

        input_df = pd.DataFrame({
            'category': [np.nan, 'http://dbpedia.org/resource/Category:2020']
        })

        expected_DG = nx.DiGraph()
        expected_nodes = ['http://dbpedia.org/resource/Category:Years', 'http://dbpedia.org/resource/Category:2020', 
                          'http://dbpedia.org/resource/Category:2020s', 'http://dbpedia.org/resource/Category:Years_in_the_future']
        expected_edges = [('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:2020s'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:Years'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:Years_in_the_future')]
        expected_DG.add_nodes_from(expected_nodes)
        expected_DG.add_edges_from(expected_edges)

        output_DG = hierarchy_graph_generator(input_df['category'], hierarchy_relation="http://www.w3.org/2004/02/skos/core#broader",
                    max_hierarchy_depth=1)

        assert nx.is_isomorphic(expected_DG, output_DG)

    def test9_skos_all_nan(self):

        input_df = pd.DataFrame({
            'category': [np.nan, np.nan]
        })

        expected_DG = nx.DiGraph()

        output_DG = hierarchy_graph_generator(input_df['category'], hierarchy_relation="http://www.w3.org/2004/02/skos/core#broader",
                    max_hierarchy_depth=1)

        assert nx.is_isomorphic(expected_DG, output_DG)

    def test10_default_behaviour_uri(self):

        input_df = pd.DataFrame({
            'value': ['http://dbpedia.org/resource/Explorair'] * 3 + ['http://dbpedia.org/resource/Buxton_Watermill'] * 2,
            'types': ['http://www.w3.org/2002/07/owl#Thing',
                      'http://dbpedia.org/ontology/Company',
                      'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Agent',
                      'http://www.w3.org/2002/07/owl#Thing',
                      'http://dbpedia.org/ontology/Place']
        })

        expected_DG = nx.DiGraph()
        expected_nodes = [
            'http://dbpedia.org/ontology/Company', 'http://dbpedia.org/ontology/Organisation', 
            'http://dbpedia.org/ontology/Place', 'http://www.w3.org/2002/07/owl#Thing', 
            'http://dbpedia.org/ontology/Agent']
        expected_edges = [
            ('http://dbpedia.org/ontology/Company', 'http://dbpedia.org/ontology/Organisation'),
            ('http://dbpedia.org/ontology/Organisation', 'http://dbpedia.org/ontology/Agent'), 
            ('http://dbpedia.org/ontology/Place', 'http://www.w3.org/2002/07/owl#Thing'), 
            ('http://dbpedia.org/ontology/Agent', 'http://www.w3.org/2002/07/owl#Thing')]
        expected_DG.add_nodes_from(expected_nodes)
        expected_DG.add_edges_from(expected_edges)

        output_DG = hierarchy_graph_generator(input_df['types'], uri_data_model=True)

        assert nx.is_isomorphic(expected_DG, output_DG)

    def test11_subclass_with_max_depth_uri(self):

        input_df = pd.DataFrame({
            'value': ['http://dbpedia.org/resource/Explorair'] * 3 + ['http://dbpedia.org/resource/Buxton_Watermill'] * 2,
            'types': ['http://www.w3.org/2002/07/owl#Thing',
                      'http://dbpedia.org/ontology/Company',
                      'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Agent',
                      'http://www.w3.org/2002/07/owl#Thing',
                      'http://dbpedia.org/ontology/Place']
        })

        expected_DG = nx.DiGraph()
        expected_nodes = [
            'http://dbpedia.org/ontology/Company', 'http://dbpedia.org/ontology/Organisation', 
            'http://dbpedia.org/ontology/Place', 'http://www.w3.org/2002/07/owl#Thing', 
            'http://dbpedia.org/ontology/Agent']
        expected_edges = [
            ('http://dbpedia.org/ontology/Company', 'http://dbpedia.org/ontology/Organisation'),
            ('http://dbpedia.org/ontology/Organisation', 'http://dbpedia.org/ontology/Agent'), 
            ('http://dbpedia.org/ontology/Place', 'http://www.w3.org/2002/07/owl#Thing'), 
            ('http://dbpedia.org/ontology/Agent', 'http://www.w3.org/2002/07/owl#Thing')]
        expected_DG.add_nodes_from(expected_nodes)
        expected_DG.add_edges_from(expected_edges)

        output_DG = hierarchy_graph_generator(input_df['types'], max_hierarchy_depth=2, uri_data_model=True)

        assert nx.is_isomorphic(expected_DG, output_DG)


    def test12_skos_broader_max_1_uri(self):

        input_df = pd.DataFrame({
            'category': ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:2020']
        })

        expected_DG = nx.DiGraph()
        expected_nodes = ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:1910s', 
                          'http://dbpedia.org/resource/Category:Years', 'http://dbpedia.org/resource/Category:2020', 
                          'http://dbpedia.org/resource/Category:2020s', 'http://dbpedia.org/resource/Category:Years_in_the_future']
        expected_edges = [('http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:1910s'), 
                          ('http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:Years'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:2020s'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:Years'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:Years_in_the_future')]
        expected_DG.add_nodes_from(expected_nodes)
        expected_DG.add_edges_from(expected_edges)


        output_DG = hierarchy_graph_generator(input_df['category'], hierarchy_relation="http://www.w3.org/2004/02/skos/core#broader",
                    max_hierarchy_depth=1, uri_data_model=True)

        assert nx.is_isomorphic(expected_DG, output_DG)

    def test13_skos_broader_max_2_uri(self):

        input_df = pd.DataFrame({
            'category': ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:2020']
        })

        expected_DG = nx.DiGraph()
        expected_nodes = ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:Years', 
                          'http://dbpedia.org/resource/Category:Chronology', 'http://dbpedia.org/resource/Category:Units_of_time', 
                          'http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:1910s', 
                          'http://dbpedia.org/resource/Category:20th_century', 'http://dbpedia.org/resource/Category:Decades', 
                          'http://dbpedia.org/resource/Category:Years_in_the_future', 'http://dbpedia.org/resource/Category:Time_periods_in_the_future', 
                          'http://dbpedia.org/resource/Category:2020s', 'http://dbpedia.org/resource/Category:21st_century', 
                          'http://dbpedia.org/resource/Category:Decades_in_the_future']
        expected_edges = [('http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:Years'), 
                          ('http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:1910s'), 
                          ('http://dbpedia.org/resource/Category:Years', 'http://dbpedia.org/resource/Category:Chronology'), 
                          ('http://dbpedia.org/resource/Category:Years', 'http://dbpedia.org/resource/Category:Units_of_time'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:Years'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:Years_in_the_future'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:2020s'), 
                          ('http://dbpedia.org/resource/Category:1910s', 'http://dbpedia.org/resource/Category:20th_century'), 
                          ('http://dbpedia.org/resource/Category:1910s', 'http://dbpedia.org/resource/Category:Decades'), 
                          ('http://dbpedia.org/resource/Category:Years_in_the_future', 'http://dbpedia.org/resource/Category:Years'), 
                          ('http://dbpedia.org/resource/Category:Years_in_the_future', 'http://dbpedia.org/resource/Category:Time_periods_in_the_future'), 
                          ('http://dbpedia.org/resource/Category:2020s', 'http://dbpedia.org/resource/Category:21st_century'), 
                          ('http://dbpedia.org/resource/Category:2020s', 'http://dbpedia.org/resource/Category:Decades'), 
                          ('http://dbpedia.org/resource/Category:2020s', 'http://dbpedia.org/resource/Category:Decades_in_the_future')]
        expected_DG.add_nodes_from(expected_nodes)
        expected_DG.add_edges_from(expected_edges)


        output_DG = hierarchy_graph_generator(input_df['category'], hierarchy_relation="http://www.w3.org/2004/02/skos/core#broader",
                    max_hierarchy_depth=2, uri_data_model=True)

        assert nx.is_isomorphic(expected_DG, output_DG)

    def test14_skos_broader_hierarchy_none_uri(self):

        input_df = pd.DataFrame({
            'category': ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:2020']
        })

        expected_DG = nx.DiGraph()
        expected_nodes = ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:1910s', 
                          'http://dbpedia.org/resource/Category:Years', 'http://dbpedia.org/resource/Category:2020', 
                          'http://dbpedia.org/resource/Category:2020s', 'http://dbpedia.org/resource/Category:Years_in_the_future']
        expected_edges = [('http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:1910s'), 
                          ('http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:Years'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:2020s'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:Years'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:Years_in_the_future')]
        expected_DG.add_nodes_from(expected_nodes)
        expected_DG.add_edges_from(expected_edges)


        output_DG = hierarchy_graph_generator(input_df['category'], hierarchy_relation="http://www.w3.org/2004/02/skos/core#broader",
                    max_hierarchy_depth=None, uri_data_model=True)

        assert nx.is_isomorphic(expected_DG, output_DG)

    
    def test15_invalid_hierarchy_relation_uri(self):

        input_df = pd.DataFrame({
            'category': ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:2020']
        })

        expected_DG = nx.DiGraph()
        expected_nodes = ['http://dbpedia.org/resource/Category:1913', 'http://dbpedia.org/resource/Category:2020']
        expected_DG.add_nodes_from(expected_nodes)

        output_DG = hierarchy_graph_generator(input_df['category'], hierarchy_relation="http://www.w3.org/2004/02/skos/ballaballa",
                    max_hierarchy_depth=None, uri_data_model=True)

        assert nx.is_isomorphic(expected_DG, output_DG)

    def test16_default_nan_uri(self):

        input_df = pd.DataFrame({
            'value': ['http://dbpedia.org/resource/Explorair'] * 3 + ['http://dbpedia.org/resource/Buxton_Watermill'] * 2,
            'types': ['http://www.w3.org/2002/07/owl#Thing',
                      np.nan,
                      'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Agent',
                      np.nan,
                      'http://dbpedia.org/ontology/Place']
        })

        expected_DG = nx.DiGraph()
        expected_nodes = ['http://dbpedia.org/ontology/Place', 
                          'http://www.w3.org/2002/07/owl#Thing']
        expected_edges = [
            ('http://dbpedia.org/ontology/Place', 'http://www.w3.org/2002/07/owl#Thing')]
        expected_DG.add_nodes_from(expected_nodes)
        expected_DG.add_edges_from(expected_edges)

        output_DG = hierarchy_graph_generator(input_df['types'], uri_data_model=True)

        assert nx.is_isomorphic(expected_DG, output_DG)

    def test17_skos_broader_nan_uri(self):

        input_df = pd.DataFrame({
            'category': [np.nan, 'http://dbpedia.org/resource/Category:2020']
        })

        expected_DG = nx.DiGraph()
        expected_nodes = ['http://dbpedia.org/resource/Category:Years', 'http://dbpedia.org/resource/Category:2020', 
                          'http://dbpedia.org/resource/Category:2020s', 'http://dbpedia.org/resource/Category:Years_in_the_future']
        expected_edges = [('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:2020s'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:Years'), 
                          ('http://dbpedia.org/resource/Category:2020', 'http://dbpedia.org/resource/Category:Years_in_the_future')]
        expected_DG.add_nodes_from(expected_nodes)
        expected_DG.add_edges_from(expected_edges)

        output_DG = hierarchy_graph_generator(input_df['category'], hierarchy_relation="http://www.w3.org/2004/02/skos/core#broader",
                    max_hierarchy_depth=1, uri_data_model=True)

        assert nx.is_isomorphic(expected_DG, output_DG)

    def test18_skos_all_nan_uri(self):

        input_df = pd.DataFrame({
            'category': [np.nan, np.nan]
        })

        expected_DG = nx.DiGraph()

        output_DG = hierarchy_graph_generator(input_df['category'], hierarchy_relation="http://www.w3.org/2004/02/skos/core#broader",
                    max_hierarchy_depth=1, uri_data_model=True)

        assert nx.is_isomorphic(expected_DG, output_DG)

