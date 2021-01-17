import re


def get_initial_query_offset(query: str):
    """Returns the OFFSET within a SPARQL query string.

    Args:
        query (str): SPARQL query string.

    Returns:
        int: Offset or 0 if no offset.
    """

    pattern = r"(OFFSET )([\d]+)"

    match = re.search(pattern, query)

    if match is None:

        return 0

    else:

        return int(match.group(2))

def get_initial_query_limit(query: str):
    """Returns the LIMIT within a SPARQL query string.

    Args:
        query (str): SPARQL query string.

    Returns:
        int: Limit or 0 if no limit.
    """

    pattern = r"(LIMIT )([\d]+)"

    match = re.search(pattern, query)

    if match is None:

        return 0

    else:

        return int(match.group(2))