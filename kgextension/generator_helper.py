import warnings
from functools import lru_cache

import networkx as nx
import numpy as np
import pandas as pd

from kgextension.endpoints import DBpedia
from kgextension.sparql_helper import endpoint_wrapper
from kgextension.utilities import link_validator
from kgextension.uri_helper import uri_querier


def get_result_df(df, result_type, prefix, merged_df, column): 
    """Helper function for unqualified and qualified relation generator. It
    helps to create the result dataframe and reduce the duplicated codes from 
    the two main functions.
    
    Arguments:
        df (pd.DataFrame):The result dataframe dummies.
        result_type (str): The type of result chosen from boolean, count, 
            relative count or tf-idf.
        prefix (str): Prefix set automatically by the generator.
        merged_df (pd.DataFrame): The original dataframe inputed by users.
        column (str): Name of the attribute containing entities that should
            be found.
    
    Returns:
        pd.DataFrame: The final dataframe.
    """

    # group values based on different tasks
    finaldf = []

    if result_type == "boolean":

        finaldf =  df.groupby("value").any().iloc[:,1:]

    elif result_type in ["count", "relative", "tfidf"]:

        finaldf =  df.groupby("value").sum()

        # If result_type is "relative" or "tfidf", calculate the relative counts per row

        if result_type in ["relative", "tfidf"]:

            # Calculate the relative counts by dividing each row by its sum, fillna(0) to replace missings created by division by zero (when sum=0)
            finaldf_relative = finaldf.copy()

            finaldf_relative = finaldf.div(finaldf.sum(axis=1), axis=0).fillna(0)

            # If result_type is "tfidf", use the table of relative counts to create the table of tfidf-values

            if result_type == "tfidf":

                # Calculate idf values

                N = len(merged_df)

                nt = finaldf[finaldf >= 1].count(axis=0)

                idf = np.log(N/nt).replace(np.inf, 0)

                # Multiply relative counts with idf values

                finaldf_relative = finaldf_relative.multiply(idf, axis="columns")

            finaldf = finaldf_relative.copy()
     
    else:
        
        raise AttributeError('Wrong result_type, try "boolean", "count", "relative" or "tfidf".')

    # add column prefix
    finaldf = finaldf.add_prefix(prefix)
    
    # adjust type   
    type_ = "int64" if result_type == "count" else ("float" if result_type in ["relative", "tfidf"] else "bool")

    finaldf = finaldf.astype(type_)

    final_col = finaldf.columns

    # merge with original df; then find and replace all NaN to 0/False
    finaldf = pd.merge(
        merged_df, finaldf, left_on=column, right_on="value", how="outer")

    if result_type == "boolean":

        finaldf[final_col] = finaldf[final_col].fillna(False)

    else:
    
        finaldf[final_col] = finaldf[final_col].fillna(0)
        
    return finaldf


def hierarchy_query_creator(
    col, hierarchy_relation, max_hierarchy_depth, uri_data_model):
    """Creates a Sparql query to retrieve the hierarchy of classes/categories. 

    Args:
        col (pd.Series): pd.Series containing the URIs.
        hierarchy_relation (str): A hierarchy relation, e.g.
            http://www.w3.org/2004/02/skos/core#broader.
        max_hierarchy_depth (int): The maximum number of hierarchy levels
            added based on the original resources. If None is passed, 
            transitive hierarchies are created, this may lead to a timeout.
        uri_data_model (bool): If false formulates query for endpoints.
        
    Returns:
        str: The SPARQL Query for hierarchy retrieval.
    """
    
    # Create Sparql "list" of the resources
    values = "(<"+col.str.cat(sep=">) (<")+">) "

    # create the hierarchy variables and add them to SELECT
    if max_hierarchy_depth and not uri_data_model:  

        # create as many variables as needed for the specified depth of the query     
        hierarchy_selectors = ["?hierarchy_selector" + str(i+1) 
            for i in range(max_hierarchy_depth)]
        variables = ["?value"] + hierarchy_selectors   
                
        query = "SELECT "+ " ".join(variables)

        if uri_data_model:
            query += " WHERE {VALUES (?value) { (<**URI**>)} "  
        else:
            query += " WHERE {VALUES (?value) {" + values + "} "

        # search for an optional superclass for each depth step
        for i in range(max_hierarchy_depth):
            query += "OPTIONAL { "+ variables[i] + " <" 
            query += hierarchy_relation + "> " + variables[i+1]+ " . } "
        query += "}"

    # else if the max_depth isnt specified search transitively. 
    else:
        if uri_data_model:
            query = "SELECT ?value ?hierarchy_selector"
            query += " WHERE {VALUES (?value) { (<**URI**>)} " 
        else:
            query = "SELECT ?value ?hierarchy_selector"
            query += " WHERE {VALUES (?value) {" + values + "} " 
        query += "OPTIONAL { ?value  <" +hierarchy_relation 
        query += "> ?hierarchy_selector . } }"
    
    return query

def create_graph_from_raw(
    DG, results, max_hierarchy_depth, current_level, uri_data_model):
    """Converts the XML obtained by the endpoint wrapper into a hierarchical
    directed graph.

    Args:
        DG (Directed Graph): The empty or preprocessed graph to be appended.
        results (DOM/pd.DataFrame): The raw results of the SPARQL query
        max_hierarchy_depth (int): The maximum number of hierarchy levels when
            the direct search is used.
        current_level (pd.Series): In case of iterative hierarchy generation
            the values of the current hierarchy level.
        uri_data_model (bool): If enabled, the URI is directly queried
            instead of a SPARQL endpoint. 

    Returns:
        nx.DirectedGraph: Graph where edges point to direct superclasses of 
        nodes.
        current_level: In case of iterative hierarchy generation the updated 
        hierarchy level.
    """

    # the uri_querier returns a dataframe with two columns, the row-wise pairs
    # are edges to be inserted into the graph
    if uri_data_model:
        # if there are no results, make sure that next level is empty and not
        # full of NA values instead
        if results.empty:
            current_level = pd.Series()
        # if no parents are found in the first iterations simply add the child
        # nodes to the graph
        elif results['hierarchy_selector'].isna().all():
            if nx.is_empty(DG):
                DG.add_nodes_from(results['value'])
            current_level = pd.Series()
        # each row-wise value-hierarchy-selector pair creates a directed edge
        # in the graph. The current level is set to the currently highest
        # parent layer.
        else:
            to_append = nx.convert_matrix.from_pandas_edgelist(
                results, 'value', 'hierarchy_selector', create_using=nx.DiGraph())
            DG = nx.compose(DG, to_append)
            current_level = results['hierarchy_selector']

    # if endpoint_wrapper is used, the graph is generated from the XML data
    else:
        for result_node in results.getElementsByTagName("result"):
            for binding in result_node.getElementsByTagName("binding"):

                attr_name = binding.getAttribute("name")

                for childnode in binding.childNodes:    
                    if childnode.firstChild is not None:
                        # get the attribute name and add it as node to the graph
                        value = childnode.firstChild.nodeValue
                        DG.add_node(value)

                        if max_hierarchy_depth:    
                            # as long as the attribute is not the base
                            # class/category, add an edge from the predecessing
                            # attribute
                                
                            if not attr_name == "value":
                                DG.add_edge(predecessing_value, value)
                            predecessing_value = value

                        else:
                            if isinstance(current_level, pd.Series):
                                current_level = list(current_level)
                            if attr_name == "value":
                                current_value = value

                            elif attr_name == "hierarchy_selector":
                                # add an edge from the lower hierarchy value to the
                                # upper hierarchy value
                                if not DG.has_edge(current_value, value):
                                    DG.add_edge(current_value, value)
                                    current_level += [value]

                # in case of the iterative search, update the values to the current
                # hierarchy level
                if not max_hierarchy_depth:
                    current_level = pd.Series(list(dict.fromkeys(current_level)))
    
    return DG, current_level
        

def hierarchy_graph_generator(
    col, 
    hierarchy_relation = "http://www.w3.org/2000/01/rdf-schema#subClassOf", 
    max_hierarchy_depth = None, endpoint = DBpedia, uri_data_model = False, progress=False, caching=True):
    """Computes a hierarchy graph from an original set of features, where 
    directed edges symbolise a hierarchy relation from subclass to superclass.

    Args:
        col (pd.Series): The classes/categories for which the hierarchy graph
            is generated.
        hierarchy_relation (str, optional): The hierarchy relation to be used.
            Defaults to "http://www.w3.org/2000/01/rdf-schema#subClassOf".
        max_hierarchy_depth (int, optional): Number of jumps in hierarchy. If 
            None, transitive jumps are used. Defaults to None.
        endpoint (Endpoint, optional): Link to the SPARQL endpoint that should
            be queried. Defaults to DBpedia.
        uri_data_model (bool, optional): whether to use sparql querier or the 
            uri data model. Defaults to False.
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process (if 
            "uri_data_model" = True). Defaults to False.
        caching (bool, optional): Turn result-caching for queries issued during 
            the execution on or off.

    Returns:
        nx.DirectedGraph: Graph where edges point to direct superclasses of
        nodes.
    """

    # warn if wrong configurations are used and correct them
    cond_subclass = hierarchy_relation ==\
         "http://www.w3.org/2000/01/rdf-schema#subClassOf"
    if  cond_subclass and max_hierarchy_depth:
        warnings.warn("""If you use subClass with a maximum hierarchy depth, 
        meaningless superclasses are generated. 
        Max_hierarchy_depth is set to None instead""")
        max_hierarchy_depth = None

    cond_broader= hierarchy_relation ==\
         "http://www.w3.org/2004/02/skos/core#broader"
    if cond_broader and max_hierarchy_depth is None:
        warnings.warn("""Transitive superclass generation does not work for
        categories. Max_hierarchy_depth is set to 1. For higher depths, set
        max_hierarchy_depth to a higher integer""")
        max_hierarchy_depth = 1
    
    # Initialise the graph
    DG = nx.DiGraph()
    # if column contains only missings return empty graph
    if col.isna().all():
        return DG
    current_level = col.copy()
    
    # in this case the query contains all future hierarchy levels and queries
    # them directly
    if max_hierarchy_depth and not uri_data_model:
        query = hierarchy_query_creator(
            col, hierarchy_relation, max_hierarchy_depth, uri_data_model) 
        results = endpoint_wrapper(query, endpoint, return_XML=True, caching=caching)
        DG, _ = create_graph_from_raw(
            DG, results, max_hierarchy_depth, None, uri_data_model)
    
    # here the "broader" steps have to be added sequentially from level to
    # level until the max_hierarchy_depth is reached
    elif max_hierarchy_depth and uri_data_model:
        hierarchy_level = 0
        while not current_level.empty and hierarchy_level<max_hierarchy_depth:
            query = hierarchy_query_creator(
                current_level, hierarchy_relation, max_hierarchy_depth, 
                uri_data_model)  
            temp_frame = pd.DataFrame(current_level)
            results = uri_querier(
                temp_frame, current_level.name, query, progress=progress, caching=caching)

            current_level=list()
            DG, current_level = create_graph_from_raw(
                DG, results, max_hierarchy_depth, current_level, 
                uri_data_model)

            hierarchy_level += 1

    # iteratively loop from hierarchy level to hierarchy level until no
    # more superclasses are found --> transitive without maximum  
    else:         
        while not current_level.empty:
            query = hierarchy_query_creator(
                current_level, hierarchy_relation, max_hierarchy_depth, 
                uri_data_model)  
            if uri_data_model:
                temp_frame = pd.DataFrame(current_level)
                results = uri_querier(
                    temp_frame, current_level.name, query, progress=progress, caching=caching)            
            else:
                results = endpoint_wrapper(query, endpoint, return_XML=True, caching=caching)
            current_level=list()
            DG, current_level = create_graph_from_raw(
                DG, results, max_hierarchy_depth, current_level, 
                uri_data_model)
    
    # Find cycles and break them
    while not nx.is_directed_acyclic_graph(DG):
        try:
            cycle = nx.find_cycle(DG)
            backwards_path = cycle[1]
            DG.remove_edge(*backwards_path)
        except nx.NetworkXNoCycle:
            pass

    return DG
  