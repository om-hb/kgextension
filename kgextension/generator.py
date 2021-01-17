from tqdm.auto import tqdm
import networkx as nx
import itertools
import re
from kgextension.endpoints import DBpedia
from kgextension.generator_helper import get_result_df, hierarchy_graph_generator
from kgextension.uri_helper import uri_querier
from kgextension.sparql_helper import regex_string_generator, endpoint_wrapper
import numpy as np
import pandas as pd
import warnings
warnings.simplefilter(action="ignore", category=UserWarning)


def data_properties_generator(df, columns, endpoint=DBpedia, uri_data_model=False, progress=True, type_filter=None, regex_filter=None, bundled_mode=True, prefix_lookup=False, caching=True):
    """Generator that takes a dataset with a link to a knowledge graph and 
    creates a new feature for each data property of the given resource.

    Args:
        df (pd.DataFrame): Dataframe to which the features will be added
        columns (str/list): Name(s) of column(s) which contain(s) the link(s) 
            to the knowledge graph.
        endpoint (Endpoint, optional): Base string to the knowledge graph; 
            ignored when "uri_data_model" = True. Defaults to DBpedia.
        uri_data_model (bool, optional): If enabled, the URI is directly 
            queried instead of a SPARQL endpoint. Defaults to False.
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True.
        type_filter (str, optional): Property datatype to be selected from 
            results (e.g. xsd:string). If a specific datatype should be
            excluded a "- " needs to be prepended (e.g. - xsd:string). Defaults
            to None.
        regex_filter (str, optional): Regular expression for filtering 
            properties. Defaults to None.
        bundled_mode (bool, optional): If True, all necessary queries are 
            bundled into one query (using the VALUES method). - Requires a 
            SPARQL 1.1 implementation! . Defaults to True.
        prefix_lookup (bool/str/dict, optional):
                        True: Namespaces of prefixes will be looked up at 
                        prefix.cc and added to the sparql query.
                        str: User provides the path to a json-file with 
                        prefixes and namespaces.
                        dict: User provides a dictionary with prefixes and 
                        namespaces.
                        Defaults to False.
        caching (bool, optional): Turn result-caching for queries issued during 
            the execution on or off. Defaults to True.

    Returns:
        pd.DataFrame: Dataframe with a new column for each property.
    """

    df = df.copy()

    # convert columns to list to enable iteration
    if not isinstance(columns, list):
        columns = [columns]

    # Prepare Type Filter Statement (Decode Include/Exclude)

    if type_filter != None:

        if type_filter[0:2] == "- ":
            type_filter_str = " && DATATYPE(?v) != " + type_filter[2:]

        else:
            type_filter_str = " && DATATYPE(?v) = " + type_filter

    # Create SPARQL query for each user-specified column

    if progress:
        iterator = tqdm(columns, desc="Column")
    else:
        iterator = columns

    for col in iterator:

        if bundled_mode and not uri_data_model:

            values = " ( <"+df[col].str.cat(sep="> ) ( <")+"> ) "

            query = "SELECT ?value ?p ?v WHERE {VALUES (?value) {" + \
                values + "} ?value ?p ?v FILTER(isLITERAL(?v)"

            if type_filter != None:

                query = query + type_filter_str

            if regex_filter != None:

                query = query + " && regex(?p, \"" + regex_filter + "\")"

            query = query + ")}"

            result_df = endpoint_wrapper(
                query, endpoint, prefix_lookup = prefix_lookup, caching=caching).drop_duplicates().reset_index(drop=True)

        else:

            result_df = pd.DataFrame()

            if uri_data_model:

                query = "SELECT DISTINCT ?value ?p ?v WHERE {VALUES (?value) {(<**URI**>)} ?value ?p ?v FILTER(isLITERAL(?v)"

                if type_filter != None:

                    query = query + type_filter_str

                if regex_filter != None:

                    query = query + " && regex(?p, \"" + regex_filter + "\")"

                query = query + ")}"

                result_df = uri_querier(df, col, query, prefix_lookup=prefix_lookup, progress=progress, caching=caching)

            else:
                for uri in df[col].iteritems():

                    if pd.notna(uri[1]):

                        query = "SELECT DISTINCT ?value ?p ?v WHERE {?value ?p ?v . FILTER (?value = <" + \
                            uri[1]+"> && (isLITERAL(?v))"

                        if type_filter != None:

                            query = query + type_filter_str

                        if regex_filter != None:

                            query = query + " && regex(?p, \"" + regex_filter + "\")"

                        query = query+")} "

                        result = endpoint_wrapper(query, endpoint, prefix_lookup=prefix_lookup, caching=caching)

                        result_df = result_df.append(result)

                    else:
                        pass

        if result_df.empty:

            pass

        else:

            # Results are transformed to a sparse dataframe (rows: looked-up uris; columns: types) with dummy-encoding (0/1) -> Each result is on row

            result_df["p"] = col + "_data_" + result_df["p"]

            # transform values into new columns

            result_df = result_df.pivot_table(
                values="v", index="value", columns="p", aggfunc=np.random.choice)

            # append properties to dataframe

            df = pd.merge(df, result_df, how="left",
                          left_on=col, right_on="value")

    return df


def direct_type_generator(df, columns, endpoint=DBpedia, uri_data_model=False, progress=True, prefix="", regex_filter=None, result_type="boolean", bundled_mode=True, hierarchy=False, prefix_lookup=False, caching=True):
    """Generator that takes a dataset with (a) link(s) to a knowledge graph and
    queries the type(s) of the linked ressources (using rdf:type). The
    resulting types are added as new columns, which are filled either with a
    boolean indicator or a count.

    Args:
        df (pd.DataFrame): Dataframe to which types are added.
        columns (str/list): Name(s) of column(s) which contain(s) the link(s) 
            to the knowledge graph.
        endpoint (Endpoint, optional): SPARQL Endpoint to be queried; ignored 
            when "uri_data_model" = True. Defaults to DBpedia.
        uri_data_model (bool, optional): If enabled, the URI is directly 
            queried instead of a SPARQL . Defaults to False.
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process . Defaults 
            to True.
        prefix (str, optional): Custom prefix for the SPARQL query. Defaults to 
            "".
        regex_filter (list, optional): A list filled with regexes (as strings) 
            to filter the results . Defaults to None.
        result_type (str, optional): States wether the results should be 
            boolean ("boolean"), counts ("counts"), relative counts 
            ("relative") or tfidf-values ("tfidf") . Defaults to "boolean".
        bundled_mode (bool, optional): If True, all necessary queries are 
            bundled into one query (using the VALUES method). - Requires a 
            SPARQL 1.1 implementation! . Defaults to True.
        hierarchy (bool, optional): If True, a hierarchy of all superclasses of 
            the returned types is attached to the resulting dataframe. Defaults 
            to False.
        prefix_lookup (bool/str/dict, optional):
                        True: Namespaces of prefixes will be looked up at 
                        prefix.cc and added to the sparql query.
                        str: User provides the path to a json-file with 
                        prefixes and namespaces.
                        dict: User provides a dictionary with prefixes and 
                        namespaces.
                        Defaults to False.
        caching (bool, optional): Turn result-caching for queries issued during 
            the execution on or off. Defaults to True.

    Returns:
        pd.DataFrame: Returns dataframe with (a) new column(s) containing the 
        found types.
    """

    df = df.copy()

    final_result_df = pd.DataFrame()

    if hierarchy:
        hierarchyGraph = nx.DiGraph()

    # convert columns to list to enable iteration
    if not isinstance(columns, list):
        columns = [columns]

    # Create SPARQL query (based on rdf:type) for each user-specified column

    if progress:
        iterator = tqdm(columns, desc="Column")
    else:
        iterator = columns

    for column in iterator:

        # If bundled_mode is selected all necessary queries for a column are bundled into one query (using the VALUES method). -> Way faster But less compatible.

        if bundled_mode and not uri_data_model:

            values = " ( <"+df[column].str.cat(sep="> ) ( <")+"> ) "

            query = prefix + \
                " SELECT DISTINCT ?value ?types WHERE {VALUES (?value) {" + \
                values+"} ?value rdf:type ?types . "

            if regex_filter != None:
                
                regex_string = regex_string_generator("?types", regex_filter)

                query = query+"FILTER("+regex_string+") "

            query = query+"}"

            result_df = endpoint_wrapper(
                query, endpoint, prefix_lookup = prefix_lookup, caching=caching).drop_duplicates().reset_index(drop=True)

        else:

            result_df = pd.DataFrame()

            if uri_data_model:

                query = prefix + \
                    " SELECT DISTINCT ?value ?types WHERE {VALUES (?value) {(<**URI**>)} ?value rdf:type ?types . "

                if regex_filter != None:

                    regex_string = regex_string_generator("str(?types)", regex_filter)

                    query = query+"FILTER("+regex_string+") "

                query = query+"}"

                result_df = uri_querier(df, column, query, prefix_lookup=prefix_lookup, progress=progress, caching=caching)

            else:

                for uri in df[column].iteritems():

                    if pd.notna(uri[1]):

                        query = prefix + \
                            " SELECT DISTINCT ?value ?types WHERE {?value rdf:type ?types . FILTER (?value = <" + \
                            uri[1]+">"

                        if regex_filter != None:

                            query = query + " && ("+regex_string_generator("?types", regex_filter)+")" 

                        query = query+") }"

                        result = endpoint_wrapper(query, endpoint, prefix_lookup=prefix_lookup, caching=caching)

                        result_df = result_df.append(result)

                    else:
                        pass

            result_df = result_df.rename(
                {"callret-0": "value"}, axis="columns").drop_duplicates().reset_index(drop=True)

        if hierarchy:
            hierarchy_col = hierarchy_graph_generator(
                result_df["types"], hierarchy_relation="http://www.w3.org/2000/01/rdf-schema#subClassOf", max_hierarchy_depth=None, endpoint=endpoint, uri_data_model=uri_data_model, progress=progress, caching=caching)

            hierarchyGraph = nx.compose(hierarchyGraph, hierarchy_col)

        if result_df.empty:

            result_columns = []
            pass

        else:

            # Results are transformed to a sparse dataframe (rows: looked-up uris; columns: types) with dummy-encoding (0/1) -> Each result is one row

            result_df_dummies = result_df.join(
                result_df.types.str.get_dummies()).drop("types", axis=1)

            # Sparse dataframe is grouped by uri

            result_df_grouped = result_df_dummies.groupby("value").sum()

            # Result columns get prefix (format depends on single or multiple columns)

            if len(columns) > 1:

                result_df_grouped = result_df_grouped.add_prefix("type_")

            else:

                result_df_grouped = result_df_grouped.add_prefix(
                    column+"_type_")

            # Results get concatenated to the queried columns (to be used as identifiers) (??)

            result_df_merged = pd.merge(
                df[columns], result_df_grouped, left_on=column, right_on="value", how="outer").drop_duplicates()

            # If multiple columns with URIs are looked up: Current results are merged with the results of previous passes of the loop

            final_result_df = pd.concat([final_result_df, result_df_merged], sort=False).groupby(
                columns, dropna=False).sum().reset_index()

            # Result columns are determined and converted to the correct dtype

            result_columns = list(
                set(list(final_result_df.columns)) - set(columns))

            final_result_df[result_columns] = final_result_df[result_columns].astype(
                "int64")

    if not final_result_df.empty:

        # If result_type is boolean, all values greater 0 are changed to True all others to False

        if result_type == "boolean":

            final_result_df[result_columns] = final_result_df[result_columns].astype(
                "bool")

        # If result_type is "relative" or "tfidf", calculate the relative counts per row

        elif result_type in ["relative", "tfidf"]:

            # Calculate the relative counts by dividing each row by its sum, fillna(0) to replace missings created by division by zero (when sum=0)
            final_result_df_relative = final_result_df.copy()

            final_result_df_relative[result_columns] = final_result_df[result_columns].div(final_result_df[result_columns].sum(axis=1), axis=0).fillna(0)

            # If result_type is "tfidf", use the table of relative counts to create the table of tfidf-values

            if result_type == "tfidf":

                # Calculate idf values

                N = len(final_result_df[result_columns])

                nt = final_result_df[result_columns][final_result_df[result_columns] >= 1].count(axis=0)

                idf = np.log(N/nt).replace(np.inf, 0)

                # Multiply relative counts with idf values

                final_result_df_relative[result_columns] = final_result_df_relative[result_columns].multiply(idf, axis="columns")

            final_result_df = final_result_df_relative.copy()

        # Collected query-results get appended to the original dataframe

        df = pd.merge(df, final_result_df, on=columns, how="outer")

    if hierarchy:
        df.attrs = {"hierarchy": hierarchyGraph}

    return df

    
def unqualified_relation_generator(
    df, columns, endpoint=DBpedia, uri_data_model=False, progress=True, 
    prefix="Link", direction="Out", regex_filter=None, result_type="boolean",
    prefix_lookup=False, caching=True):
    """Unqualified relation generator creates attributes from the existence of 
    relations and adds boolean, counts, relative counts or tfidf-values features
    for incoming and outgoing relations.

    Args:
        df (pd.DataFrame): Dataframe to which links are added.
        columns (str/list): Name(s) of column(s) which contain(s) the link(s) 
            to the knowledge graph.
        endpoint (Endpoint, optional): SPARQL Endpoint to be queried; ignored 
            when "uri_data_model" = True. Defaults to DBpedia.
        uri_data_model (bool, optional): If enabled, the URI is directly 
            queried instead of a SPARQL endpoint. Defaults to False.
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True.
        prefix (str, optional): Custom prefix for the SPARQL query. Defauls to 
            "Link".
        direction (str, optional): The direction for properties which choose 
            from Incoming, Outgoing (In and Out). Defaults to "Out".
        regex_filter (str, optional): Regular expression for filtering 
            properties. Defaults to None.
        result_type (str, optional): States wether the results should be 
            boolean ("boolean"), counts ("counts"), relative counts 
            ("relative") or tfidf-values ("tfidf") Defaults to "boolean".
        prefix_lookup (bool/str/dict, optional):
                        True: Namespaces of prefixes will be looked up at 
                        prefix.cc and added to the sparql query.
                        str: User provides the path to a json-file with 
                        prefixes and namespaces.
                        dict: User provides a dictionary with prefixes and 
                        namespaces.
                        Defaults to False.
        caching (bool, optional): Turn result-caching for queries issued during 
            the execution on or off. Defaults to True.

    Returns:
        pd.DataFrame: Dataframe with new columns containing the links of 
        properties to the knowledge graph
    """

    df = df.copy()

    #convert columns to list to enable iteration
    if not isinstance(columns, list):

        columns = [columns]

    #iterate over possibly several link columns
    if progress:
        iterator = tqdm(columns, desc="Column")
    else:
        iterator = columns

    for col in iterator:  

        if not uri_data_model: 

            values = " ( <"+df[col].str.cat(sep="> ) ( <")+"> ) "

            if direction == "Out":

                query = "SELECT DISTINCT ?value ?p ?o WHERE {VALUES (?value) {" + values + "} ?value ?p ?o "

            elif direction == "In": 

                query = "SELECT DISTINCT ?value ?p ?s WHERE {VALUES (?value) {" + values + "} ?s ?p ?value "

            if regex_filter != None:

                regex_string = regex_string_generator("?p", regex_filter)

                query = query+"FILTER("+regex_string+") "

            query = query+"}"

            result_df = endpoint_wrapper(query, endpoint, prefix_lookup=prefix_lookup, caching=caching).drop_duplicates().reset_index(drop=True)  

        else:

            if direction == "Out":

                query = "SELECT DISTINCT ?value ?p ?o WHERE {VALUES (?value) { (<**URI**>)} ?value ?p ?o "

            elif direction == "In": 

                query = "SELECT DISTINCT ?value ?p ?s WHERE {VALUES (?value) { (<**URI**>)} ?s ?p ?value "

            if regex_filter != None:

                regex_string = regex_string_generator("str(?p)", regex_filter)

                query = query+"FILTER("+regex_string+") "

            query = query+"}"

            result_df = uri_querier(df, col, query, prefix_lookup=prefix_lookup, progress=progress, caching=caching) 

    if type(result_df) != type(pd.DataFrame()):

        pass

    if result_df.empty :

        pass

    else:

        result_df_dummies = result_df.join(result_df["p"].str.get_dummies()).drop("p",axis=1)

        result_df = get_result_df(result_df_dummies, 
                                  result_type, 
                                  prefix+"_"+direction+"_"+result_type+"_",
                                  df, 
                                  columns)

    return result_df


def qualified_relation_generator(
    df, columns, endpoint=DBpedia, uri_data_model=False, progress=True, 
    prefix="Link", direction="Out", properties_regex_filter=None, 
    types_regex_filter=None, result_type="boolean", hierarchy=False, 
    prefix_lookup=False, caching=True):
    """Qualified relation generator considers not only relations, but also the 
    related types, adding boolean, counts, relative counts or tfidf-values 
    features for incoming and outgoing relations.

    Args:
        df (pd.DataFrame): Dataframe to which links are added.
        columns (str/list): Name(s) of column(s) which contain(s) the link(s) 
            to the knowledge graph.
        endpoint (Endpoint, optional): SPARQL Endpoint to be queried; ignored 
            when "uri_data_model" = True. Defaults to DBpedia.
        uri_data_model (bool, optional): If enabled, the URI is directly 
            queried instead of a SPARQL endpoint. Defaults to False.
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True.
        prefix (str, optional): Custom prefix for the SPARQL query. Defauls to 
            "Link".
        direction (str, optional): The direction for properties which choose 
            from Incoming, Outgoing (In and Out). Defaults to "Out".
        properties_regex_filter (str, optional): Regular expression for 
            filtering properties. Defaults to None.
        types_regex_filter (str, optional): Regular expression for filtering 
            types. Defaults to None.
        result_type (str, optional): States wether the results should be 
            boolean ("boolean"), counts ("counts"), relative counts 
            ("relative") or tfidf-values ("tfidf") Defaults to "boolean".
        hierarchy (bool, optional): If True, a hierarchy of all superclasses of 
            the returned types is attached to the resulting dataframe. Defaults 
            to False.
        prefix_lookup (bool/str/dict, optional):
                        True: Namespaces of prefixes will be looked up at 
                        prefix.cc and added to the sparql query.
                        str: User provides the path to a json-file with 
                        prefixes and namespaces.
                        dict: User provides a dictionary with prefixes and 
                        namespaces.
                        Defaults to False.
        caching (bool, optional): Turn result-caching for queries issued during 
            the execution on or off. Defaults to True.

    Returns:
        pd.DataFrame: Dataframe with new columns containing the links of properties to the knowledge graph
    """

    df = df.copy()  

    if hierarchy:
        hierarchyGraph = nx.DiGraph()

    #convert columns to list to enable iteration
    if not isinstance(columns, list):

        columns = [columns]

    #iterate over possibly several link columns
    if progress:
        iterator = tqdm(columns, desc="Column")
    else:
        iterator = columns

    for col in iterator:

        if not uri_data_model:

            values = " ( <"+df[col].str.cat(sep="> ) ( <")+"> ) "

            if direction == "Out":

                query = "SELECT ?value ?p ?o ?type WHERE {VALUES (?value) {" + values + "} ?value ?p ?o. ?o rdf:type ?type. "

            elif direction == "In": 

                query = "SELECT ?value ?p ?s ?type WHERE {VALUES (?value) {" + values + "} ?s ?p ?value. ?s rdf:type ?type. "

            if properties_regex_filter != None:

                regex_string = regex_string_generator("?p", properties_regex_filter)

                query = query+"FILTER("+regex_string+") "

            if types_regex_filter != None:

                regex_string = regex_string_generator("?type", types_regex_filter)

                query = query+"FILTER("+regex_string+") "

            query = query+"}"

            result_df = endpoint_wrapper(query, endpoint, prefix_lookup=prefix_lookup, caching=caching).drop_duplicates().reset_index(drop=True)

        else:

            if direction == "Out":

                query = "SELECT ?value ?p ?o ?type WHERE {VALUES (?value) {(<**URI**>)} ?value ?p ?o. ?o rdf:type ?type. "

            elif direction == "In": 

                query = "SELECT ?value ?p ?s ?type WHERE {VALUES (?value) {(<**URI**>)} ?s ?p ?value. ?s rdf:type ?type. " 

            if properties_regex_filter != None:

                regex_string = regex_string_generator("str(?p)", properties_regex_filter)

                query = query+"FILTER("+regex_string+") "                

            if types_regex_filter != None:

                regex_string = regex_string_generator("str(?type)", types_regex_filter)

                query = query+"FILTER("+regex_string+") "

            query = query+"}"

            result_df = uri_querier(df, col, query, prefix_lookup=prefix_lookup, progress=progress, caching=caching) 

    if type(result_df) != type(pd.DataFrame()):

        pass

    if result_df.empty :

        pass

    else:
        if hierarchy:

            hierarchy_col = hierarchy_graph_generator(result_df["type"], hierarchy_relation="http://www.w3.org/2000/01/rdf-schema#subClassOf",max_hierarchy_depth=None, endpoint=endpoint, uri_data_model=uri_data_model, progress=progress, caching=caching)

            hierarchyGraph = nx.compose(hierarchyGraph, hierarchy_col)

        result_df["link_with_type"] = result_df["p"] + "_type_" + result_df["type"]

        result_df = result_df[["value","link_with_type"]]

        result_df_dummies = result_df.join(result_df["link_with_type"].str.get_dummies()).drop("link_with_type",axis=1) 

        result_df = get_result_df(result_df_dummies, 
                            result_type, 
                            prefix+"_"+direction+"_"+result_type+"_",
                            df,
                            columns)  

    if hierarchy:  
        # append hierarchy to df as attribute, this will generate a warning but works
        result_df.attrs = {"hierarchy": hierarchyGraph}

    return result_df
            
        
def specific_relation_generator(
    df, columns, endpoint=DBpedia, uri_data_model=False, progress=True, 
    direct_relation="http://purl.org/dc/terms/subject", 
    hierarchy_relation=None, max_hierarchy_depth=1, prefix_lookup=False, caching=True):
    """Creates attributes from a specific direct relation. Additionally, it is
    possible to append a hierarchy with a user-defined hierarchy relation.

    Args:
        df (pd.DataFrame): the dataframe to extend
        columns (str/list): Name(s) of column(s) which contain(s) the link(s) 
            to the knowledge graph.
        endpoint (Endpoint, optional): SPARQL Endpoint to be queried; ignored
            when "uri_data_model" = True. Defaults to DBpedia.
        uri_data_model (bool, optional): If enabled, the URI is directly queried
            instead of a SPARQL endpoint. Defaults to False.
        progress (bool, optional): If True, progress bars will be shown to
            inform the user about the progress made by the process. Defaults 
            to True.
        direct_relation (str, optional): Direct relation used to create
            features. Defaults to "http://purl.org/dc/terms/subject".
        hierarchy_relation (str, optional): Hierarchy relation used to connect 
            categories, e.g. http://www.w3.org/2004/02/skos/core#broader. 
            Defaults to None.
        max_hierarchy_depth (int, optional): Maximal number of hierarchy steps
            taken. Defaults to 1.
        prefix_lookup (bool/str/dict, optional):
                        True: Namespaces of prefixes will be looked up at 
                        prefix.cc and added to the sparql query.
                        str: User provides the path to a json-file with 
                        prefixes and namespaces.
                        dict: User provides a dictionary with prefixes and 
                        namespaces.
                        Defaults to False.
        caching (bool, optional): Turn result-caching for queries issued during 
            the execution on or off. Defaults to True.

    Returns:
        pd.DataFrame: The dataframe with additional features.
    """

    df = df.copy()
        
    if hierarchy_relation:
        hierarchy_relation = re.sub(r"^.*?https://", "http://", hierarchy_relation)
        hierarchy = nx.DiGraph()

    direct_relation = re.sub(r"^.*?https://", "http://", direct_relation)
    
    # convert columns to list to enable iteration
    if not isinstance(columns, list):
        columns = [columns]

    if df[columns].isna().all().item():
        return df

    #  iterate over possibly several link columns
    if progress:
        iterator = tqdm(columns, desc="Column")
    else:
        iterator = columns

    for col in iterator:

        if not uri_data_model:
            # Create Sparql Query
            values = "(<"+df[col].str.cat(sep=">) (<")+">) "
            query = "SELECT  ?value ?object "
            query += " WHERE {VALUES (?value) {" + values 
            query += "} ?value (<" + direct_relation + ">) ?object. }"

            # Retrieve query results from endpoint
            query_result = endpoint_wrapper(
                query, endpoint, prefix_lookup=prefix_lookup, caching=caching).\
                    drop_duplicates().reset_index(drop=True)
        else:
            # Create URI Query 
            query = "SELECT ?value ?object WHERE {VALUES (?value) {(<**URI**>)}"
            query += " ?value (<" + direct_relation + ">) ?object. }"
                
            query_result = uri_querier(
                df, col, query, prefix_lookup=prefix_lookup, progress=progress, caching=caching)

        # delete empty columns (for example when hierarchy relation returns
        # nothing)
        query_result = query_result.dropna(how="all", axis=1)

        # check if there are valid results, if not return the original frame
        if query_result.empty:
            continue

        # extract hierarchy
        if hierarchy_relation:
            hierarchy_col = hierarchy_graph_generator(
                query_result["object"], hierarchy_relation=hierarchy_relation,
                max_hierarchy_depth=max_hierarchy_depth, endpoint=endpoint, 
                uri_data_model=uri_data_model, progress=progress, caching=caching)
            hierarchy = nx.compose(hierarchy, hierarchy_col)

        query_grouped = query_result.groupby("value")["object"].apply(list)

        # bundle the unique new features
        new_cols = pd.Series(query_grouped.values.sum()).unique()

        # create shape of result dataframe to fill
        df_to_append = pd.DataFrame(columns=new_cols)
        df_to_append["value"] = query_grouped.index

        # check for each URI if it belongs to the category and tick True/False
        for row, new_col in itertools.product(df_to_append.index, new_cols):
            df_to_append.loc[row, new_col] = np.where(
                new_col in query_grouped[df_to_append.loc[row, "value"]], 
                True, False).item()

        # merge the new column with the original dataframe
        df_to_append.rename({"value": col}, axis=1, inplace=True)
        df = pd.merge(df, df_to_append, how="left", on=col)

        # rename columns
        if new_cols.any():
            df.columns = [
                col + "_in_boolean_" + name 
                if name in new_cols else name 
                for name in df.columns]

    # append hierarchy to df as attribute, this will generate a warning but
    # works
    if hierarchy_relation:
        df.attrs = {"hierarchy": hierarchy}

    return df


def custom_sparql_generator(df, link_attribute, query, endpoint=DBpedia, progress=True, attribute_generation_strategy="first", prefix_lookup=False, caching=True):
    """This generator issues a custom SPARQL query and creates additional 
    attributes from the query results.

    Args:
        df (pd.DataFrame): Dataframe to which links are added
        link_attribute (str): Name of column containing the link to the 
            knowledge graph.
        query (str): Custom SPARQL query which returns attributes to be 
            appended.
        endpoint (Endpoint, optional): SPARQL Endpoint to be queried; ignored
            when "uri_data_model" = True. Defaults to DBpedia.
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True.
        prefix_lookup (bool/str/dict, optional):
                        True: Namespaces of prefixes will be looked up at 
                        prefix.cc and added to the sparql query.
                        str: User provides the path to a json-file with 
                        prefixes and namespaces.
                        dict: User provides a dictionary with prefixes and 
                        namespaces.
                        Defaults to False.
        caching (bool, optional): Turn result-caching for queries issued during 
            the execution on or off. Defaults to True.

    Returns:
        pd.DataFrame: Dataframe with new columns containing the query results.
    """

    # TODO: Add attribute generation strategy to Docstring

    variable = re.search(r"\*.*\*", query).group().replace("*", "")

    var_index = df.columns.get_loc(variable)

    df_result = pd.DataFrame()

    if progress:
        iterator = tqdm(df.iterrows(), total=df.shape[0], desc="Row")
    else:
        iterator = df.iterrows()

    for row in iterator:

        query_temp = re.sub(
            r"\*.*\*", "<" + str(row[1].iloc[var_index]) + ">", query)

        df_temp = pd.DataFrame([row[1].iloc[var_index]],
                               columns=["link_attribute"])
        
        df_temp = pd.concat([df_temp,endpoint_wrapper(query_temp, endpoint, caching=caching).head(1)], axis=1)

        df_result = pd.concat([df_result, df_temp],
                              ignore_index=True, sort=True)

    df = pd.merge(df, df_result.drop_duplicates(),
                  left_on=link_attribute, right_on="link_attribute", how="left")
    df.drop("link_attribute", axis=1, inplace=True)

    return df
