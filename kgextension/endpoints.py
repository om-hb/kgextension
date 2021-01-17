from kgextension.sparql_helper import RemoteEndpoint

DBpedia = RemoteEndpoint(url = "http://dbpedia.org/sparql", timeout=120, requests_per_min=100*60, retries=10, page_size=10000)

"""   
Predefined SPARQL endpoint for DBpedia.

Settings:

    ResultSetMaxRows           = 10000;
    MaxQueryExecutionTime      =   120  (seconds);
    MaxQueryCostEstimationTime =  1500  (seconds);
    Connection limit           =    50  (parallel connections per IP address);
    maximum request rate       =   100  (requests per second per IP address, with an initial burst of 120 requests)

NOTE: Queries which time out will return PARTIAL results in a best effort
fashion, and will NOT return an error.

Source. https://wiki.dbpedia.org/public-sparql-endpoint
"""

WikiData = RemoteEndpoint(url = "https://query.wikidata.org/bigdata/namespace/wdq/sparql", timeout=60, requests_per_min=100000, retries=1, page_size=0)

"""
Predefined SPARQL endpoint for WikiData.

NOTE: A user-specific user agent header is needed (https://meta.wikimedia.org/wiki/User-Agent_policy) -> Use "agent" argument! 

There is a hard query deadline configured which is set to 60 seconds. There are also following limits:

    One client (user agent + IP) is allowed 60 seconds of processing time each 60 seconds
    One client is allowed 30 error queries per minute

Clients exceeding the limits above are throttled with HTTP code 429. Use Retry-After header to see when the request can be repeated. If the client ignores 429 responses and continues to produce requests over the limits, it can be temporarily banned from the service. 
Clients who don’t comply with the User-Agent policy may be blocked completely – make sure to send a good User-Agent header.

Every query will timeout when it takes more time to execute than this configured deadline. You may want to optimize the query or report a problematic query here.

Also note that currently access to the service is limited to 5 parallel queries per IP. The above limits are subject to change depending on resources and usage patterns. 

Source: https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual#Query_limits
"""


EUOpenData = RemoteEndpoint(url = "https://data.europa.eu/euodp/sparqlep", timeout=180, requests_per_min=100000, retries=10, page_size=0)

"""
Predefined SPARQL endpoint for the EU Open Data Portal (EU ODP).

No Usage Policy found?

Source: https://data.europa.eu/euodp/en/developerscorner
"""


#----------------------------------

# -> Paralell Queries per IP address
# -> Paralell Connections per IP address
# -> Error Queries
# -> Processing Time per XY
# -> Use Retry-After header -> https://stackoverflow.com/questions/61803586/wikidata-forbidden-access