import pandas as pd
import numpy as np
import re
from tqdm.auto import tqdm
from kgextension.uri_helper import uri_querier


def link_explorer(df, base_link_column, number_of_hops = 1, links_to_follow = ["owl:sameAs"], lod_sources = [], exclude_sources = [], prefix_lookup=False, progress = True, caching=True):
    """Follows the defined links starting from a base link to a certain number 
    of hops. Adds the discovered links as new columns to the dataframe.

    Args:
        df (pd.DataFrame): Dataframe with a base link
        base_link_column (str): Name of column which contains the base link to  
            start with. 
        number_of_hops (int, optional): Depth of exlporation of the LOD cloud. 
            Defaults to 1.
        links_to_follow (list, optional): Names of links that should be 
            followed. Defaults to "owl:sameAs".
        lod_sources (list, optional): Restrict exploration to certain datasets. 
            Use strings or regular expressions to define the allowed datasets. 
            Defaults to [].
        exclude_sources (list, optional): Exclude certain datasets from 
            exploration. Use strings or regular expressions to define the 
            datasets. Defaults to [].
        prefix_lookup (bool/str/dict, optional):
                        True: Namespaces of prefixes will be looked up at 
                        prefix.cc and added to the sparql query.
                        str: User provides the path to a json-file with 
                        prefixes and namespaces.
                        dict: User provides a dictionary with prefixes and 
                        namespaces.
                        Defaults to False.
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True.
        caching (bool, optional): Turn result-caching for queries issued during 
            the execution on or off. Defaults to True.
            
    Returns:
        pd.DataFrame: Dataframe with a new column for each discovered link.
    """
    
    if not isinstance(links_to_follow, list):
        links_to_follow = [links_to_follow]

    if not isinstance(exclude_sources, list):
        exclude_sources = [exclude_sources]

    if not isinstance(lod_sources, list):
        lod_sources = [lod_sources]
        
    all_links = list(df[base_link_column])

    query_raw = " SELECT DISTINCT ?value ?uri{} WHERE {{VALUES (?value) {{(<**URI**>)}} ?value " + "|".join(links_to_follow) + " ?uri{} }} "
    
    df_merged = pd.DataFrame()
    df_all = pd.DataFrame()

    if progress:
        iterator = tqdm(
            range(1,number_of_hops+1), desc="Link Explorer - Performing Hops.")
    else:
        iterator = range(1,number_of_hops+1)
    
    for hop in iterator: 

        query = query_raw.format(str(hop),str(hop))
        
        if hop == 1:
            df_result = uri_querier(df, base_link_column, query, prefix_lookup=prefix_lookup, caching=caching, progress=progress)
        else:
            df_result = uri_querier(df_result, "uri"+str(hop-1), query, prefix_lookup=prefix_lookup, caching=caching, progress=progress)

        if df_result.empty:
            break
        
        # eliminate duplicate links
        df_result = df_result[~df_result["uri"+str(hop)].isin(all_links)]

        # filter sources               
        if lod_sources:
            df_result = df_result[df_result["uri"+str(hop)].str.contains("|".join(lod_sources))]

        # exclude certain sources defined by string or regex  
        if exclude_sources:
            df_result = df_result[~df_result["uri"+str(hop)].str.contains("|".join(exclude_sources))]

        if df_result.empty:
            break

        if df_merged.empty:
            df_merged = df_result
        else:
            df_merged = pd.merge(df_merged, df_result, left_on="uri"+str(hop-1), right_on="value", how="left", suffixes=("", "_y")).drop("value_y",axis=1)    

        df_all = df_all.append(df_merged[["value","uri"+str(hop)]].rename(columns={"uri"+str(hop) : "uri"}))
        df_all = df_all.dropna().drop_duplicates()
        
        all_links += df_result["uri"+str(hop)].tolist()

    if df_all.empty:
        return df
            
    df_all["count"] = np.nan

    regex_pattern = "^http:/"

    while True:

        regex_pattern += "/[^/]*"

        df_all["pld"] = df_all.apply(
            lambda x: x["pld"] if x["count"] == 1 else re.search(r"{}".format(regex_pattern), x["uri"]).group(), axis=1)

        df_all = df_all.drop("count", axis=1)

        df_with_counts = df_all.groupby(["value","pld"]).size().reset_index(name="count")

        df_all = pd.merge(df_all, df_with_counts, left_on=["value","pld"], right_on=["value","pld"])

        #break loop when all counts are 1
        if (df_all["count"] == 1).all():
            break

    df_pivot = df_all.pivot_table(values="uri", index="value", columns="pld", aggfunc="first").reset_index()
    
    df_final = pd.merge(df, df_pivot, left_on=base_link_column, right_on="value", how="outer").drop("value",axis=1)    
    
    return df_final