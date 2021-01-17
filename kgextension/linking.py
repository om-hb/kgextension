import urllib.parse
import string

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

from kgextension.endpoints import DBpedia
from kgextension.linking_helper import (dll_query_resolver,
                                        spotlight_uri_extractor)
from kgextension.sparql_helper import endpoint_wrapper, regex_string_generator
from kgextension.uri_helper import uri_querier
from kgextension.utilities import check_uri_redirects


def pattern_linker(
    df, column, new_attribute_name="new_link", progress=True, 
    base_url="http://dbpedia.org/resource/", url_encoding=True, 
    DBpedia_link_format=True):
    """Basic Pattern Linker that takes attributes from a column and a base link
    and generates a new column with the respective knowledge graph links.

    Args:
        df (pd.DataFrame): Dataframe to which links are added.
        column (str): Name of column whose entities should be found.
        new_attribute_name (str, optional): Name of column containing the link 
            to the knowledge graph. Defaults to "new_link".
        progress (bool, optional): If True, progress updates will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True. 
        base_url (str, optional): Base string to the knowledge graph. Defaults 
            to "www.dbpedia.org/resource/".
        url_encoding (bool, optional): Enables automatic url encoding. Defaults 
            to True.
        DBpedia_link_format (bool, optional): Enables conversion to DBpedia 
            link format. Defaults to True.

    Returns:
        pd.DataFrame: Dataframe with a new column containing the links to the
        knowledge graph.
    """

    if progress:
        print("Pattern Linker - Generating URIs")

    df = df.copy()

    if DBpedia_link_format:

        df[column] = df[column].apply(lambda x: string.capwords(x, sep = None)) 

        df[new_attribute_name] = base_url + df[column]

        df[new_attribute_name] = df[new_attribute_name].str.replace(" ", "_")

    else:
        df[new_attribute_name] = base_url + df[column]


        ### TODO: Add more functionality here! (Ask Paulheim, Bizer, etc.) ###

    if url_encoding:
        #df[new_attribute_name] = df[new_attribute_name].apply(lambda x:
        #urllib.parse.quote)
        
        df[new_attribute_name] = df[new_attribute_name].apply(
            lambda x: np.nan if pd.isna(x) else urllib.parse.quote(x, safe=":/"))

    return df


def dbpedia_lookup_linker(
    df, column, new_attribute_name="new_link", progress=True, 
    base_url="https://lookup.dbpedia.org/api/search/", max_hits=1, 
    query_class="", lookup_api="KeywordSearch", caching=True):
    """Implementation of the DBpedia Lookup service
    (https://github.com/dbpedia/lookup). Takes strings from a column, looks for
    matching DBPedia entities and returns their URIs to newly added columns. 

    Args:
        df (pd.DataFrame): Dataframe to which links are added.
        column (str): Name of the attribute containing entities that should
            be looked up.
        new_attribute_name (str, optional): Name of column / prefix of columns
            containing the link to the knowledge graph. Defaults to "new_link".
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True.
        base_url (str, optional): Set the base URL for the generation of 
            request URLs. Defaults to "https://lookup.dbpedia.org/api/search/".
        max_hits (int, optional): Maximal number of URIs that should be 
            returned per entity. Defaults to 1.
        query_class (str, optional): A DBpedia class from the DBpedia Ontology 
            (https://wiki.dbpedia.org/services-resources/ontology) that the 
            results should have (without prefix, e.g., dbo:place as place). 
            Defaults to "".
        lookup_api (str, optional): Choose between KeywordSearch and 
            PrefixSearch mode of DBpedia Lookup. Defaults to "KeywordSearch".
        caching (bool, optional): Turn result-caching for lookups issued during 
            the execution on or off. Defaults to True

    Returns:
        pd.DataFrame: Returns dataframe with (a) new column(s) containing the
        links to the DBpedia entities.
    """

    df = df.copy()

    # Build the base-link for the API query, based on the provided inputs.

    base_link = base_url + lookup_api + "?" 
    
    if query_class == "":

        pass

    else:

        base_link = base_link + "QueryClass=" + query_class

    base_link = base_link + "&MaxHits=" + str(max_hits) + "&QueryString="

    # Create the actual query-links and add them to the provided dataframe.

    df["dll_query_link"] = base_link + df[column]

    # Create a list that contains the column names for the columns that are to
    # be created.
    
    column_names = []

    if max_hits > 1:
        for i in range(max_hits):
            column_names.append(new_attribute_name+"_"+str(i+1))

    else:
        column_names.append(new_attribute_name)

    # Use the dll_query_resolver helper-function to transform the generated
    # query-links into columns in the dataframe that contain the URIs of found
    # ressources.

    if progress:
        tqdm.pandas(desc="DBpedia Lookup Linker: Querying DLL")
        if caching:
            df[column_names] = df.progress_apply(lambda x: dll_query_resolver(x["dll_query_link"], max_hits), axis=1)
        else:
            df[column_names] = df.progress_apply(lambda x: dll_query_resolver.__wrapped__(x["dll_query_link"], max_hits), axis=1)
    else:
        if caching:
            df[column_names] = df.apply(lambda x: dll_query_resolver(x["dll_query_link"], max_hits), axis=1)
        else:
            df[column_names] = df.apply(lambda x: dll_query_resolver.__wrapped__(x["dll_query_link"], max_hits), axis=1)

    # Drop the column containing the intermediate query_link.

    df.drop("dll_query_link", axis=1, inplace=True)

    # Drop columns that were created but couldn't be filled (except the base column).

    if max_hits > 1:

        for column in df[column_names[1:]]:

            if len(df[column].value_counts()) == 0:

                df.drop(column, axis=1, inplace=True)

    # Return resulting dataframe

    return df


def label_linker(
    df, column, new_attribute_name="new_link", progress=True, endpoint=DBpedia, result_filter=None,
    language="en", max_hits=1, label_property="rdfs:label",prefix_lookup=False, caching=True):
    """Label Linker takes attributes from a column and adds a new column with
    the respective knowledge graph links based on the provided label_property
    (rdfs:label by default).

    Args:
        df (pd.DataFrame): Dataframe to which links are added.
        column (str): Name of the column whose entities should be found.
        new_attribute_name (str, optional): Name of column containing the link 
            to the knowledge graph. Defaults to "new_link".
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True.
        endpoint (Endpoint, optional): Choose SPARQL endpoint connection. 
            Defaults to DBpedia.
        result_filter (list, optional): A list filled with regexes (as strings) 
            to filter the results. Defaults to None.
        language (str, optional): Restrict search to labels with a certain 
            language tag. Set to None if restriction is needed. Defaults to 
            "en".
        max_hits (int, optional): Maximal number of URI's that should be 
            returned per entity. Defaults to 1.
        label_property (str, optional): Specifies the label_property the should 
            be used in the query. Defaults to "rdfs:label".
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
        pd.DataFrame: Dataframe with a new column containing the links to the
        knowledge graph.
    """

    df = df.copy()

    result_df = pd.DataFrame()

    if progress:
        iterator = tqdm(df[column].iteritems(), total=df.shape[0])
    else:
        iterator = df[column].iteritems()

    for col in iterator:

        if not pd.isnull(col[1]):
            query = "SELECT DISTINCT ?label ?uri WHERE { ?uri "+label_property+" ?label . filter"

            if language != None:

                query = query + "(?label =\"" + col[1] + "\"@" + language

            else:

                query = query + "(str(?label) =\"" + col[1] + "\""
                
            if result_filter != None:

                query = query + \
                        " && ("+regex_string_generator("?uri",
                                                        result_filter)+")"

            query = query + ")}"
            
            if max_hits:
                query = query + " LIMIT " + str(max_hits)

            result = endpoint_wrapper(query, endpoint, prefix_lookup=prefix_lookup, caching=caching)
            result_df = result_df.append(result)

    result_df = result_df.reset_index(drop=True)

    if result_df.empty:

        df[new_attribute_name+"_1"] = np.nan

        return df

    else:

        result_df_grouped = result_df.groupby("label")["uri"].apply(
            lambda x: pd.Series(x.values)).unstack()
        result_df_grouped = result_df_grouped.rename(
            columns={i: "new_link"+"_{}".format(i + 1) for i in range(result_df_grouped.shape[1])})
        result_df_grouped = result_df_grouped.reset_index()

        df = pd.merge(df, result_df_grouped.drop_duplicates(), left_on=column,
                      right_on="label", how="outer").drop("label", axis=1)

    return df


def dbpedia_spotlight_linker(
    df, column, new_attribute_name="new_link", progress=True, max_hits=1, 
    language="en", selection="first", confidence=0.3, support=5, 
    min_similarity_score=0.5, caching=True):
    """Implementation of the DBpedia Spotlight Service
    (https://www.dbpedia-spotlight.org/). Takes strings from a column, looks
    for linked Wikipedia entities and returns their URIs to newly added
    columns.

    Args:
        df (pd.DataFrame): Dataframe to which links are added.
        column (str): Name of the column whose entities should be found.
        new_attribute_name (str, optional): Name of column containing the link 
            to the knowledge graph. Defaults to "new_link".
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True.
        max_hits (int, optional): Maximal number of URI's that should be 
            returned per entity. Defaults to 1.
        language (str, optional): The DBPedia language setting. Defaults to
            "en".
        selection (str, optional): Specifies whether the entities that occur 
            first (first), that have the highest support(support) or that have 
            the highest similarity score(similarityScore) should be chosen. 
            Defaults to "first".
        confidence (float, optional): Confidence threshold. Defaults to 0.3.
        support (int, optional): Support threshold. Defaults to 5.
        min_similarity_score (float, optional): Minimal similarity threshold.
            Defaults to 0.5.
        caching (bool, optional): Turn result-caching for queries issued during 
            the execution on or off. Defaults to True.   

    Returns:
        pd.DataFrame: Returns dataframe with (a) new column(s) containing the
            DBPedia URIs.
    """

    df = df.copy()

    assert selection in [
        "first", "support", "similarityScore"], \
            "Selection has to be first, support or similarity score"

    link = "https://api.dbpedia-spotlight.org/" + language + "/annotate"

    # Create a list that contains the column names for the columns that are to
    # be created.
    
    column_names = [new_attribute_name+"_" + str(i+1) 
                    if max_hits > 1 else new_attribute_name 
                    for i in range(max_hits)]
                    
    # Use the extract_uris helper-function to find URIS from the column entries
    # and insert them into new columns.
    if progress:
        tqdm.pandas(desc="DBpedia Spotlight Linker: Querying DSL")
        if caching:
            df[column_names] = df.progress_apply(lambda x: spotlight_uri_extractor(x[column], link, max_hits, selection, confidence, support, min_similarity_score), axis=1, result_type="expand")
        else:
            df[column_names] = df.progress_apply(lambda x: spotlight_uri_extractor.__wrapped__(x[column], link, max_hits, selection, confidence, support, min_similarity_score), axis=1, result_type="expand")

    else:
        if caching:
            df[column_names] = df.apply(lambda x: spotlight_uri_extractor(x[column], link, max_hits, selection, confidence, support, min_similarity_score), axis=1, result_type="expand")
        else:
            df[column_names] = df.apply(lambda x: spotlight_uri_extractor.__wrapped__(x[column], link, max_hits, selection, confidence, support, min_similarity_score), axis=1, result_type="expand")

    # Drop columns that were created but couldn't be filled .
    if not max_hits == 1:
        df.dropna(axis=1, how="all", inplace=True)

    # Return resulting dataframe
    return df


def sameas_linker(
    df, column, new_attribute_name="new_link", progress=True, endpoint=DBpedia, 
    result_filter=None, uri_data_model=False, bundled_mode=True, 
    prefix_lookup=False, caching=True):
    """Function that takes URIs from a column of a DataFrame and queries a
    given SPARQL endpoint for ressources which are connected to these URIs via
    owl:sameAs. Found ressources are added as new columns to the dataframe and
    the dataframe is returned.

    Args:
        df (pd.DataFrame): Dataframe to which links are added.
        column (str): Name of the column for whose entities links should be
            found.
        new_attribute_name (str, optional): Name / prefix of the column(s)  
            containing the found links. Defaults to "new_link".
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process (if 
            "uri_data_model" = True). Defaults to True.
        endpoint (Endpoint, optional): SPARQL Endpoint to be queried; ignored 
            when "uri_data_model" = True. Defaults to DBpedia.
        result_filter (list, optional): A list filled with regexes (as strings) 
            to filter the results. Defaults to None.
        uri_data_model (bool, optional): If enabled, the URI is directly 
            queried instead of a SPARQL endpoint. Defaults to False.
        bundled_mode (bool, optional): If True, all necessary queries are   
            boundled into one querie (using the VALUES method). - Requires a 
            SPARQL 1.1 implementation!. Defaults to True.
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
        found ressources.
    """

    df = df.copy()

    if bundled_mode and not uri_data_model:

        values = " ( <"+df[column].str.cat(sep="> ) ( <")+"> ) "

        query = " SELECT DISTINCT ?value ?sameas_uris WHERE {VALUES (?value) {" + \
            values+"} ?value owl:sameAs ?sameas_uris . "

        if result_filter != None:

            query = query + \
                "FILTER("+regex_string_generator("?sameas_uris", result_filter)+") "

        query = query+"}"

        result_df = endpoint_wrapper(
            query, endpoint, prefix_lookup=prefix_lookup, caching=caching).drop_duplicates()

    else:

        result_df = pd.DataFrame()

        if uri_data_model:

            query = " SELECT DISTINCT ?value ?sameas_uris WHERE {VALUES (?value) {(<**URI**>)} ?value owl:sameAs ?sameas_uris . "

            if result_filter != None:

                query = query + \
                    "FILTER("+regex_string_generator("str(?sameas_uris)",
                                                     result_filter)+") "

            query = query+"}"

            result_df = uri_querier(
                df, column, query, prefix_lookup=prefix_lookup, progress=progress, caching=caching)

        else:

            if progress:
                iterator = tqdm(df[column].iteritems(), total=df.shape[0])
            else:
                iterator = df[column].iteritems()

            for uri in iterator:

                if pd.isna(uri[1]):

                    pass

                else:

                    query = " SELECT DISTINCT ?value ?sameas_uris WHERE {?value owl:sameAs ?sameas_uris. FILTER (?value = <"+uri[
                        1]+">"

                    if result_filter != None:

                        query = query + \
                            " && ("+regex_string_generator("?sameas_uris",
                                                           result_filter)+")"

                    query = query+") }"

                    result = endpoint_wrapper(query, endpoint, prefix_lookup=prefix_lookup, caching=caching)

                    result_df = result_df.append(result)

        result_df = result_df.rename(
            {"callret-0": "value"}, axis="columns").drop_duplicates().reset_index(drop=True)

    if result_df.empty:

        df[new_attribute_name+"_1"] = np.nan

        return df

    else:

        result_df_grouped = result_df.groupby("value")

        result_df_grouped = result_df_grouped["sameas_uris"].apply(
            lambda x: pd.Series(x.values)).unstack()
        result_df_grouped = result_df_grouped.rename(
            columns={i: new_attribute_name+"_{}".format(i + 1) for i in range(result_df_grouped.shape[1])})

        df = pd.merge(df, result_df_grouped, left_on=column,
                      right_on="value", how="outer")

        return df
