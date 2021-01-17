import pandas as pd
import numpy as np
from tqdm.auto import tqdm
from kgextension.utilities_helper import is_valid_url, url_exists
from kgextension.endpoints import DBpedia
from kgextension.sparql_helper import endpoint_wrapper
from kgextension.uri_helper import uri_querier


def link_validator(df, columns, purge=True, custom_name_postfix=None, fill_with=np.NaN, caching = True, progress=True):
    """Takes a column of URLs / URIs from a DataFrame and checks for each if it 
    is resolvable. If not it's either replaced with some user-specified entry 
    or a flag is added to a newly generated column.

    Args:
        df (pd.DataFrame): Dataframe for which the links should be inspected.
        columns (list): List containing the names of the columns in the 
            DataFrame, that contain the links.
        purge (bool, optional): If True: Links that are not resolvable will be 
            replaced with "fill_with"; If False: A new column, containing the 
            result for each link in boolean format, is added to the DataFrame. 
            Defaults to True.
        custom_name_postfix (str, optional): Custom postfix for the newly 
            created column (in case "purge" is set to False). Defaults to None.
        fill_with (flexible, optional): Specifies what not resolvable links 
            should be replaced with (in case "purge" is set to True). Defaults 
            to np.NaN.
        caching (bool, optional): Turn result caching on or off. Defaults to 
            True.
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True.

    Raises:
        ValueError: Raised if 'custom_name_postfix' is set to "" instead of 
            None.

    Returns:
        pd.DataFrame: Returns dataframe with cleaned links / a new column.
    """
    
    if custom_name_postfix == "":

        raise ValueError("'custom_name_postfix' can't be an empty string. If you don't want to use a custom_name_postfix, please set the attribute to None")
    
    if type(columns) == str:

        columns = [columns]

    df = df.copy()

    if not isinstance(columns, list):
        columns = [columns]

    if progress:
        iterator = tqdm(columns, desc="Link Validator: Column", leave=True)
    else:
        iterator = columns

    for column in iterator:

        if custom_name_postfix == None:
            new_attribute_name = column+"_exists"

        else:
            new_attribute_name = column+custom_name_postfix

        if progress:
            tqdm.pandas(desc="Link Validator: Link", leave=False)
            if caching:
                df[new_attribute_name] = df[column].progress_apply(url_exists)
            else:
                df[new_attribute_name] = df[column].progress_apply(lambda x: url_exists.__wrapped__(x))
        else:
            if caching:
                df[new_attribute_name] = df[column].apply(url_exists)
            else:
                df[new_attribute_name] = df[column].apply(lambda x: url_exists.__wrapped__(x))

        if purge:

            df.loc[df[new_attribute_name] == False, column] = fill_with
            df.drop(new_attribute_name, axis=1, inplace=True)

    return df


def check_uri_redirects(df, column, replace=True, custom_name_postfix=None, redirection_property="http://dbpedia.org/ontology/wikiPageRedirects", endpoint=DBpedia, regex_filter="dbpedia", bundled_mode=True, uri_data_model=False, progress=True, caching=True):
    """Takes a column of URIs from a DataFrame and checks for each if it has a 
    redirection set by the endpoint. If this is the case, the URI it redirects 
    to is either added in a new column or replaces the original URI.

    Args:
        df (pd.DataFrame): Dataframe for which the URIs should be inspected.
        column (str): Name of the column that contains the URIs that should be 
            checked.
        replace (bool, optional): If True: URIs that get redirected will be 
            replaced with the new URI; If False: A new column, containing the 
            result for each URI, is added to the DataFrame. Defaults to True.
        custom_name_postfix (str, optional): Custom postfix for the newly 
            created column (in case "replace" is set to False). Defaults to None.
        redirection_property (str, optional): Relation/Property URI that 
            signals a redirect for this endpoint. Defaults to 
            "http://dbpedia.org/ontology/wikiPageRedirects".
        endpoint (Endpoint, optional): SPARQL Endpoint to be queried; ignored 
            when "uri_data_model" = True. Defaults to DBpedia.
        regex_filter (str, optional): Just URIs matching the specified RegEx 
            are checked for redirects. Defaults to "dbpedia".
        bundled_mode (bool, optional): If True, all necessary queries are 
            bundled into one query (using the VALUES method). - Requires a 
            SPARQL 1.1 implementation!; ignored when "uri_data_model" = True. 
            Defaults to True.
        uri_data_model (bool, optional): If enabled, the URI is directly 
            queried instead of a SPARQL endpoint. Defaults to False.
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process (if 
            "uri_data_model" = True). Defaults to True.
        caching (bool, optional): Turn result-caching for queries issued during 
            the execution on or off. Defaults to True.

    Raises:
        ValueError: Raised if 'custom_name_postfix' is set to "" instead of 
            None.

    Returns:
        pd.DataFrame: Returns dataframe with cleaned links / a new column.
    """

    if custom_name_postfix == "":

        raise ValueError("'custom_name_postfix' can't be an empty string. If you don't want to use a custom_name_postfix, please set the attribute to None")

    df = df.copy()

    if bundled_mode and not uri_data_model:

        values = " ( <"+df[column].str.cat(sep="> ) ( <")+"> ) "

        query = "SELECT DISTINCT ?value ?redirect WHERE {VALUES (?value) {" +values+"} ?value <"+redirection_property+"> ?redirect . }"

        result_df = endpoint_wrapper(query, endpoint, caching=caching).drop_duplicates().reset_index(drop=True)

    else:   
        
        result_df = pd.DataFrame()
        
        if uri_data_model:
            
            query = "SELECT DISTINCT ?value ?redirect WHERE {VALUES (?value) {(<**URI**>)} ?value <"+redirection_property+"> ?redirect . }"

            result_df = uri_querier(df, column, query, regex_filter=regex_filter, progress=progress, caching=caching)
            
        else:

            for uri in df[column].iteritems():

                if pd.notna(uri[1]):

                    query = "SELECT DISTINCT ?value ?redirect WHERE {?value <"+redirection_property+"> ?redirect . FILTER (?value = <"+uri[1]+">) }"

                    result = endpoint_wrapper(query, endpoint, caching=caching)

                    result_df = result_df.append(result)

                else:
                    pass

        result_df = result_df.rename({"callret-0": "value"}, axis="columns").drop_duplicates().reset_index(drop=True)

    if result_df.empty:

        return df

    else:

        if custom_name_postfix == None:

            new_attribute_name = column+"_redirect"

        else:

            new_attribute_name = column+custom_name_postfix

        result_df = pd.merge(df, result_df, how="left", left_on=column, right_on="value").drop("value",axis=1).rename(columns={"redirect":new_attribute_name})

        if replace:

            result_df.loc[(pd.isnull(result_df[new_attribute_name])), new_attribute_name] = result_df[column]
            result_df.drop(column, axis=1, inplace=True)
            result_df.rename(columns={new_attribute_name: column}, inplace=True)

    return result_df