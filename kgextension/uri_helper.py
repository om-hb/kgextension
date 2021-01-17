from bs4 import BeautifulSoup
from rdflib import Graph
from rdflib.plugins.sparql.results.csvresults import CSVResultSerializer
from functools import lru_cache
import pandas as pd
import numpy as np
import requests
import bs4
import re
import io
import urllib.error
import urllib.parse
import json
import re
import urllib.request
import warnings
import xml
from tqdm.auto import tqdm


@lru_cache(maxsize=None)
def query_uri_logic(uri, query_string, return_format):
    """Parsing & querying logic of the "query_uri" function. Detached from the 
    main function for caching purposes.

    Args:
        uri (str): Dereferencable URI.
        query_string (str): SPARQL query (the URI should already be inserted 
            via the values statement).
        return_format (dict): Used to set specific return formats for data 
            sources (if the default "application/rdf+xml" is not supported). 
            For supported formats see: 
            https://rdflib.readthedocs.io/en/stable/plugin_parsers.html. 

    Returns:
        pd.DataFrame : Result of the SPARQL query issued against the URI.
    """

    graph = Graph()
    graph.parse(urllib.parse.quote(uri, safe=":/"), format=return_format)
    query_result = graph.query(query_string)

    serializer = CSVResultSerializer(query_result)
    io_module = io.BytesIO()
    serializer.serialize(io_module)

    return pd.read_csv(io.StringIO(io_module.getvalue().decode("utf-8")))


def query_uri(uri, query_string, return_formats = {"wikidata.org": "n3"}, verbose = True, caching=True):
    """Function that allows to query a given dereferencable URI with a given 
    SPARQL query, without the need for an SPARQL endpoint.

    Args:
        uri (str): Dereferencable URI.
        query_string (str): SPARQL query (the URI should already be inserted 
            via the values statement).
        return_formats (dict, optional): Used to set specific return formats 
            for data sources (if the default "application/rdf+xml" is not 
            supported). For supported formats see:
            https://rdflib.readthedocs.io/en/stable/plugin_parsers.html. 
            Defaults to {"wikidata.org": "n3"}.
        verbose (bool, optional): Turn on/off warnings for likely malformed     
            URIs. Defaults to True.
        caching (bool, optional): Turn result caching on or off. Defaults to 
            True.

    Returns:
        pd.DataFrame : Result of the SPARQL query issued against the URI. If 
        the provided URI is NULL, then a empty dataframe is returned.
    """

    if uri == "" or pd.isnull(uri):

        return pd.DataFrame()
    
    else:

        try:
    
            return_format = "application/rdf+xml"

            for source in return_formats.keys():

                if source in uri:
                    return_format = return_formats[source]
                    break

                else:
                    pass

            if caching:
                result = query_uri_logic(uri, query_string, return_format)
            else:
                result = query_uri_logic.__wrapped__(uri, query_string, return_format)

            return result

        except urllib.error.URLError:

            if verbose:
                warnings.warn(uri + " is not a valid URI.")
            return pd.DataFrame()

        except FileNotFoundError:

            if verbose:
                warnings.warn(uri + " might not be a valid URI.")
            return pd.DataFrame()

        except xml.sax.SAXParseException:

            if verbose:
                warnings.warn(uri + " might not be dereferencable.")
            return pd.DataFrame()

        except TypeError:

            if verbose:
                warnings.warn(uri + " might not be dereferencable.")
            return pd.DataFrame()

        except Exception as exception:

            if verbose:
                warnings.warn("Following exception was raised during the querying of URI " + uri + ":"+str(exception))
            return pd.DataFrame()
    

def uri_querier(df, column, query, regex_filter = None, return_formats = {"wikidata.org": "n3"}, verbose = True, caching = True, prefix_lookup=False, progress= True):
    """Wrapper function for the query_uri function. Queries each URI in a specified column of a DataFrame with a user-provided query and returns the results as one joint DataFrame.

    Args:
        df (pd.DataFrame): DataFrame that contains the URIs that should be 
            queried.
        column (str): Column in the specified DataFrame that contains the URIs 
            that should be queried.
        query (str): The SPARQL query that's used for querying the URIs. Has to 
            contain a single placehold (**URI**) in the VALUES statement. 
            Example: "SELECT ?value ?p ?o WHERE {VALUES (?value) { (<**URI**>)} 
            ?value ?p ?o }"
        regex_filter (str, optional): If set, just URIs matching the specified 
            RegEx are queried. Defaults to None.
        return_formats (dict, optional): Used to set specific return formats 
            for data sources (if the default "application/rdf+xml" is not 
            supported). For supported formats see: 
            https://rdflib.readthedocs.io/en/stable/plugin_parsers.html. 
            Defaults to {"wikidata.org": "n3"}.
        verbose (bool, optional): Turn on/off warnings for likely malformed 
            URIs. Defaults to True.
        caching (bool, optional): Turn result caching on or off. Defaults to 
            True.
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
            
    Returns:
        pd.DataFrame: Joint DataFrame that contains the query-results of all 
        URIs.
    """

    results = []

    if progress:
        iterator = tqdm(df[column], leave=False, desc="URI")
    else:
        iterator = df[column]

    if prefix_lookup:
        
        if prefix_lookup == True:

            with urllib.request.urlopen("http://prefix.cc/context") as url:
                namespace_prefixes = json.loads(url.read().decode())["@context"]

        elif isinstance(prefix_lookup, str):

            with open(prefix_lookup) as file: 
                namespace_prefixes = json.load(file)

        elif isinstance(prefix_lookup, dict):

            namespace_prefixes = prefix_lookup

        # get all prefixes from query
        query_prefixes = re.findall('[a-z0-9-]+(?=[:{1}][a-zA-Z0-9]+)',query)

        #add namespaces to query
        query = "".join(["PREFIX " + str(x) + ": <" + namespace_prefixes[x]
            + "> " for x in query_prefixes if x in namespace_prefixes.keys()]) + query

    for uri in iterator:

        if pd.isna(uri):

            results.append(pd.DataFrame())

        elif regex_filter == None:

            specific_query = query.replace("**URI**",uri)
            result = query_uri(uri, specific_query, return_formats, caching=caching)
            results.append(result)

        else:

            if re.search(regex_filter, uri) == None:

                results.append(pd.DataFrame())

            else:

                specific_query = query.replace("**URI**",uri)
                result = query_uri(uri, specific_query, return_formats, caching=caching)
                results.append(result)

    result_df = pd.concat(results, ignore_index=True) 
    
    return result_df
