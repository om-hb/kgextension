import requests
import validators
import warnings
import pandas as pd
from functools import lru_cache


def is_valid_url(url):
    """Checks if a URL is in proper format.

    Args:
        url (str): The URL that should be checked.

    Returns:
        bool: Result of the validity check in boolean form.
    """

    valid = validators.url(url)
    if valid:
        return True
    else:
        return False

@lru_cache(maxsize=None)
def url_exists(url):
    """Checks if a URL is resolvable / existing.

    Args:
        url (str): The URL that should be checked.

    Returns:
        bool: Result of the resolvability check in boolean form.
    """
    
    if not pd.isnull(url):
        if is_valid_url(url):
            try:
                with requests.get(url, stream=True) as response:
                    try:
                        response.raise_for_status()
                        return True
                    except requests.exceptions.HTTPError:
                        return False
            except requests.exceptions.ConnectionError:
                return False
        else:
            warnings.warn("Warning: The url "+url +
                        " could not be resolved due to improper formatting / syntax!")
            return False
    else:
        return False
