from SPARQLWrapper import SPARQLWrapper, CSV, JSON, XML, POSTDIRECTLY, POST, __agent__
import warnings
import pandas as pd
import io
import time
import json
import re
import urllib.request
from rdflib import Graph, util
from ratelimit import limits, sleep_and_retry
from functools import lru_cache

from kgextension.sparql_helper_helper import get_initial_query_offset, get_initial_query_limit


def regex_string_generator(attribute, filters, logical_connective = "OR"):
    """#TODO

    Args:
        attribute ([type]): [description]
        filters ([type]): [description]
        logical_connective (str, optional): [description]. Defaults to "OR".

    Raises:
        ValueError: [description]

    Returns:
        [type]: [description]
    """
    
    rules = []
    
    for rule in filters:
    
        rules.append("regex("+attribute+", \""+rule+"\")")

    if logical_connective == "OR":

        regex_string = " || ".join(rules)

    elif logical_connective == "AND":

        regex_string = " && ".join(rules)

    else:
        raise ValueError("Allowed inputs for logical_connective: \"OR\"; \"AND\"")
    
    return regex_string    
    

class Endpoint():
    """Base Endpoint class.
    """
    pass


class RemoteEndpoint(Endpoint):
    """RemoteEndpoint class, that handles remote SPARQL endpoints.
    """
    
    def __init__(self, url, timeout=60, requests_per_min = 100000, retries=10, page_size=0, supports_bundled_mode=True, persistence_file_path="rate_limits.db", agent=__agent__):
        """Configuration of a SPARQL Endpoint.

        Args:
            url (str): URL of the endpoint.
            timeout (int, optional): Defines the time which the endpoint is 
                given to respond (in seconds). Defaults to 60.
            requests_per_min (int, optional): Defines the maximal number of  
                requests per minute. Defaults to 100000.
            retries (int, optional): Defines the number of times a query is 
                retried. Defaults to 10.
            page_size (int, optional): Limits the page size of the results, 
                since many endpoints have limitations. Defaults to 0.
            supports_bundled_mode (boolean, optional): If true, bundled mode 
                will be used to query the endpoint. Defaults to True.
            persistence_file_path (str, optional): Sets the file path for the 
                database that keeps track of past query activities (to comply 
                with usage policies). Defaults to "rate_limits.db".
            agent (str, optional): The User-Agent for the HTTP request header. 
                Defaults to SPARQLWrapper.__agent__.
        """
        
        self.url = url
        self.timeout = timeout
        self.requests_per_min = requests_per_min
        self.retries = retries
        self.page_size = page_size
        self.supports_bundled_mode = supports_bundled_mode
        self.persistence_file_path = persistence_file_path
        self.query = sleep_and_retry(limits(calls=requests_per_min, period=60, storage=self.persistence_file_path, name='"'+url+'"')(self._query))
        self.agent = agent
    
    def _query(self, query, request_return_format = "XML", verbose = False, return_XML=False):
        """Function that queries a user-specified remote SPARQL endpoint with a 
        user-specified query and returnes the results as a pandas DataFrame.
        
        Args:
            query (str): Query that should be sent to the SPARQL endpoint.
            request_return_format (str, optional): Requesting a specific return 
                format from the SPARQL endpont (str) - mainly for debugging and 
                testing. Defaults to "XML".
            verbose (bool, optional): Set to True to let the function print 
                additional information about the returned data - for debugging 
                and testing. Defaults to False.
            return_XML (bool, optional): If True it returns the XML results 
                instead of a dataframe. Defaults to False.
        
        Raises:
            RuntimeError: Is returned when the returned data is neither a XML, 
            CSV or JSON, for whatever reason.
        
        Returns:
            pd.DataFrame: The query results in form of a DataFrame.
        """

        retries_count = 0
        while True:
            
            try:
                sparql = SPARQLWrapper(self.url, agent=self.agent)
                sparql.setRequestMethod(POSTDIRECTLY)
                sparql.setMethod(POST)
                sparql.setTimeout(self.timeout)
                
                sparql.setQuery(query)
                return_formats = {"XML": XML, "CSV": CSV, "JSON": JSON}
                requested_format = return_formats[request_return_format]

                # Catch RuntimeWarning that is raised by SPARQLWrapper when retunred and requested format do not match.

                with warnings.catch_warnings():

                    warnings.filterwarnings("ignore",category=RuntimeWarning)

                    # Try to query with ReturnFormat that is requested through requested_format and check which format is returned

                    sparql.setReturnFormat(requested_format)
                    results_raw = sparql.query()

                    returned_content_type = results_raw.info()["content-type"]

                    if verbose:

                        print(returned_content_type)

                # If the returned format is XML, query with requested ReturnFormat = XML and process accordingly

                if "application/sparql-results+xml" in returned_content_type:

                    results = results_raw.convert()

                    if return_XML:
                        return results

                    result_dict = {}
                    result_index = 0

                    for result_node in results.getElementsByTagName("result"):

                        temp_result_dict = {}

                        for binding in result_node.getElementsByTagName("binding"):

                            attr_name = binding.getAttribute("name")

                            for childnode in binding.childNodes:

                                if childnode.firstChild is not None:
                                    value = childnode.firstChild.nodeValue
                                    temp_result_dict.update({attr_name: value})


                        result_dict[result_index] = temp_result_dict

                        result_index += 1

                    return pd.DataFrame.from_dict(result_dict, orient="index")

                # If the returned format is JSON, query with requested ReturnFormat = JSON and process accordingly

                elif "application/sparql-results+json" in returned_content_type:

                    results = sparql.query().convert()

                    results_df = pd.DataFrame(results["results"]["bindings"])
                    results_df = results_df.applymap(lambda x: x["value"])

                    return results_df

                # If the returned format is CSV, query with requested ReturnFormat = CSV and process accordingly

                elif "text/csv" in returned_content_type:

                    results = results_raw.convert()

                    results = io.BytesIO(results)

                    return pd.read_csv(results, delimiter=",", dtype=str)

                # If the returned format is neither XML, CSV or JSON, raise RuntimeError

                else:

                    raise RuntimeError("The results format returned by the SPARQL endpoint ("+returned_content_type+") is not supported!")
                
                break
                
            except Exception as e: 
                
                retries_count+=1
                if retries_count > self.retries:
                    print(e)
                    break
                time.sleep(1)


class LocalEndpoint(Endpoint):
    """LocalEndpoint class, that handles access to local RDF files.
    """

    def __init__(self, file_path, file_format = "auto"):
        """Class to allow working with local RDF files. Turns the local file
        into a LocalEndpoint. Should support: html, hturtle, mdata, microdata
        n3, nquads, nt, rdfa, rdfa1.0, rdfa1.1, trix, turtle, xml.

        Args:
            file_path (str): Path of the local RDF file.
            file_format (str, optional): Option to specify the file format of 
                the local file. If set to "auto", the function will try to 
                automatically determine the format. For more info see: 
                https://rdflib.readthedocs.io/en/stable/plugin_parsers.html  
                Defaults to "auto".
        """
  
        #if is_local_file:
        
        self.file_path = file_path
        self.file_format = file_format

    def initialize(self):
        """Initializing the LocalEndpoint, i.e. loading the data into memory.
        """

        g = Graph()
    
        if self.file_format == "auto":
        
            format_guess = util.guess_format(self.file_path)
        
            g.parse(self.file_path, format=format_guess)
        
        else:
        
            g.parse(self.file_path, format=self.file_format)
        
        self.endpoint = g
    
    def close(self):
        """Closing the LocalEndpoint, i.e. releasing the data from memory.
        """

        self.endpoint = None

    def query(self, query):
        """Function to issue a query against a LocalEndpoint.

        Args:
            query (str): SPARQL query.

        Returns:
            pd.DataFrame: The query results as DataFrame.
        """
    
        results = self.endpoint.query(query)

        results_csv = io.StringIO(str(results.serialize(format="csv"),"utf-8")) 

        return pd.read_csv(results_csv)


def endpoint_wrapper(query: str, endpoint: Endpoint, request_return_format = "XML", verbose = False, return_XML = False, prefix_lookup=False, caching=True):
    """Wrapper function for sparql-querier and local rdf-files.
    
    Args:
        query (str): Query that should be sent to the SPARQL endpoint
        endpoint (Endpoint): Link to the SPARQL endpoint that should be queried.
        request_return_format (str, optional): Requesting a specific return 
            format from the SPARQL endpoint. Defaults to "XML".
        verbose (bool, optional): Set to True to let the function print 
            additional information about the returned data - for
            debugging and testing. Defaults to False.
        return_XML (bool, optional): if True it returns the XML results instead 
            of a dataframe. Defaults to False.
        prefix_lookup (bool/str/dict, optional):
                        True: Namespaces of prefixes will be looked up at 
                        prefix.cc and added to the sparql query.
                        str: User provides the path to a json-file with 
                        prefixes and namespaces.
                        dict: User provides a dictionary with prefixes and 
                        namespaces.
                        Defaults to False.
        caching (bool, optional): Turn result caching on or off. Defaults to 
            True.

    Returns:
        pd.DataFrame: The query results in form of a DataFrame.
    """

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

    if caching:
        return endpoint_wrapper_logic(query = query, endpoint = endpoint, request_return_format = request_return_format, verbose = verbose, return_XML = return_XML)
    else:
        return endpoint_wrapper_logic.__wrapped__(query = query, endpoint = endpoint, request_return_format = request_return_format, verbose = verbose, return_XML = return_XML)


@lru_cache(maxsize=None)
def endpoint_wrapper_logic(query, endpoint, request_return_format, verbose, return_XML):
    """This is a helper function for "endpoint_wrapper", outsourced for caching purposes. Not intended for end-user usage. #TODO: Schöner lösen?
    """

    if isinstance(endpoint, LocalEndpoint):

        return endpoint.query(query)

    elif isinstance(endpoint, RemoteEndpoint):
        
        query_limit = get_initial_query_limit(query)
        
        query_offset = get_initial_query_offset(query)
        
        if query_limit > 0:
            
            #user defined limit is used as maximum number of results
            max_results = query_limit + query_offset
            
            if query_limit > endpoint.page_size:
                
                query_limit = endpoint.page_size
        else:
            max_results = 0
            
            query_limit = endpoint.page_size
        
        if query_limit > 0:
            
            df_result = pd.DataFrame()
            
            #delete limit and offset from query
            query = query.split("OFFSET")[0]
            query = query.split("LIMIT")[0]
            while True:
                
                if max_results > 0:
                    
                    #check if max_results reached
                    if query_offset >= max_results:
                        return df_result
                
                    elif query_offset + query_limit > max_results:
                    
                        query_limit = max_results - query_offset
                
                query = query.split("LIMIT")[0] + "LIMIT " + str(query_limit) + " OFFSET " + str(query_offset)
                    
                query_offset += query_limit
                
                query_result = endpoint.query(query, request_return_format, verbose, return_XML)
                if return_XML:
                    return query_result
                if query_result.empty:
                    return df_result
                else:
                    df_result = df_result.append(query_result)
                    df_result = df_result.reset_index(drop=True).reindex(index=range(len(df_result)))
                            
        else:
            return endpoint.query(query, request_return_format, verbose, return_XML)

    else:

        raise TypeError("The object passed to the function as endpoint is not of a supported Type (i.e. a LocalEndpoint or RemoteEndpoint object) but instead is a: "+str(type(endpoint)))