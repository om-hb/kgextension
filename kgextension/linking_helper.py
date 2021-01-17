import pandas as pd
from lxml import etree
import numpy as np
import requests
import spotlight
from urllib.error import HTTPError
from functools import lru_cache


@lru_cache(maxsize=None)
def dll_query_resolver(query_link, maxHits):
    """Resolves a query link for the DBpedia Lookup API to a series of the URIs 
    returned for that query.
    
    Args:
        query_link (str): API request in link form.
        maxHits (int): Maximal number of URIs that should be returned by the 
            API.
    
    Returns:
        pd.Series: Containing the URIs as strings.
    """
    
    # Check if query_link is empty
    
    if pd.isnull(query_link) or query_link.endswith("&QueryString="):
        
        return pd.Series(dtype="float64")
    
    else:

        # Parse XML file from the provided link.

        root = etree.fromstring(requests.get(query_link).content)
      
        # Converte the located URIs to string and add them to a list.

        results_as_str = []

        for result_index in range(len(root)):

            results_as_str.append(root[result_index][1].text)

        # If the number of resulting URIs < maxHits - pad the list with NaNs.

        if len(results_as_str) < maxHits:

            for _ in range(maxHits-len(results_as_str)):

                results_as_str.append(np.nan)

        # Return the resulting list as pandas series.

        return pd.Series(results_as_str)


@lru_cache(maxsize=None)
def spotlight_uri_extractor(entry, link, max_hits=1, selection="first", confidence=0.5, support=20,
                            min_similarity_score=0.8):
    """Finds linked DBPedia entities of a string and returns them as a list.

    Args:
        entry (str): Text in which entities are to be found.
        link (str): Link to DBPedia Spotlight.
        max_hits (int, optional): Maximal number of URIs that should be 
            returned per entity. Defaults to 1.
        selection (str, optional): Specifies whether the entities that occur 
            first (first), that have the highest support(support) or that have 
            the highest similarity score(similarityScore) should be chosen. 
            Defaults to "first".
        confidence (float, optional): #TODO. Defaults to 0.5.
        support (int, optional): #TODO. Defaults to 20.
        min_similarity_score (float, optional): #TODO. Defaults to 0.8.

    Returns:
        list: All URIs found in accordance with the parameters. If max_hits > 
        found URIs the list is filled with NAs.
    """

    if not isinstance(entry, str):
        return [np.nan] * max_hits

    # get all annotations in accordance with the specified confidence and support
    try:
        annotations = pd.DataFrame(
            spotlight.annotate(link, entry, confidence=confidence, support=support)
        )
    except spotlight.SpotlightException:
        annotations = pd.DataFrame(
            columns = ["URI", "support", "types", "surfaceForm", "offset",
                       "similarityScore", "percentageOfSecondRank"])

    if annotations.empty:
        return [np.nan] * max_hits

    # drop all annotations below the minimum similarity score
    annotations = annotations[annotations["similarityScore"]>= min_similarity_score]

    # for support or similarity score selection, sort the annotations
    if selection in ["support", "similarityScore"]:
        annotations = annotations.sort_values(selection, ascending=False).reset_index(drop=True)
        
    # extract URIs from the annotation results
    uris = list(annotations.loc[:max_hits-1, "URI"])
    len_uris = len(uris)

    # fill up list with NAs to comply with max_hits length
    if max_hits > len_uris:
        for _ in range(max_hits-len_uris):
            uris.append(np.nan)

    # return the top max_hits annotations
    return uris
