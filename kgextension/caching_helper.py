import pandas as pd
from collections import OrderedDict
from functools import wraps
from kgextension.utilities_helper import url_exists
from kgextension.sparql_helper import endpoint_wrapper_logic
from kgextension.uri_helper import query_uri_logic
from kgextension.linking_helper import (dll_query_resolver,
                                        spotlight_uri_extractor)

def show_cache_info():
    """Function that gives the user an overview over the status of all cached 
    methods.
    """

    print("query_uri_logic: "+str(query_uri_logic.cache_info()))
    print("endpoint_wrapper_logic: "+str(endpoint_wrapper_logic.cache_info()))
    print("dll_query_resolver: "+str(dll_query_resolver.cache_info()))
    print("spotlight_uri_extractor: "+str(spotlight_uri_extractor.cache_info()))
    print("url_exists: "+str(url_exists.cache_info()))


def clear_cache():
    """Function that clears the cache of all cached methods when it's called.
    """

    query_uri_logic.cache_clear()
    endpoint_wrapper_logic.cache_clear()
    dll_query_resolver.cache_clear()
    spotlight_uri_extractor.cache_clear()
    url_exists.cache_clear()    


def freeze_unhashable(freeze_by="argument", freeze_argument=None, freeze_index=None):
    """Wrapper function to "freeze" a unhashable function attribute (dictionary
    or pandas Series) into a hashable OrderedDict. Used for functions that need
    to be cached but have these types of arguments as inputs.

    Args: 
        freeze_by (str, optional): Used to indicate whether the argument that
            needs to be freezed is selected via its argument name ("argument") 
            or its index ("index"). Defaults to "argument".
        freeze_argument (str, optional): Name of the argument that should be
            freezed. Used if freeze_by = "argument". Defaults to None.
        freeze_index (int, optional): Index of the argument that should be
            freezed. Used if freeze_by = "index". Defaults to None.
    """

    def outer_decorator(fn):
        @wraps(fn)
        def inner_decorator(*args, **kwargs):

            if freeze_by == "argument":

                if freeze_argument in kwargs.keys():

                    if type(kwargs[freeze_argument]) == pd.Series:

                        kwargs[freeze_argument] = (tuple(kwargs[freeze_argument].to_dict(OrderedDict).items()), kwargs[freeze_argument].name)

                    elif type(kwargs[freeze_argument]) == dict:
                        
                        kwargs[freeze_argument] = tuple(OrderedDict(kwargs[freeze_argument]).items())

                    else:
                        pass

                else:
                    pass

            elif freeze_by == "index":

                args_updated=[]

                for i in range(len(args)):

                    if i != freeze_index:

                        args_updated.append(args[i])

                    else:

                        if type(args[i]) == pd.Series:

                            args_updated.append((tuple(args[i].to_dict(OrderedDict).items()), args[i].name))

                        elif type(args[i]) == dict:

                            args_updated.append(tuple(OrderedDict(args[i]).items()))

                        else:

                            args_updated.append(args[i])

                args = tuple(args_updated)

            response = fn(*args, **kwargs)

            return response
        return inner_decorator
    return outer_decorator


def unfreeze_unhashable(frozen_argument, frozen_type="series"):
    """Function to "unfreeze" unhashable arguments "frozen" by the
    freeze_unhashable function.

    Args: 
        frozen_argument (tuple/OrderedDict): The frozen argument. Pandas Series 
            as tuple and dictionaries as OrderedDict.
        frozen_type (str, optional): Indicator whether the frozen arguemnt is a
            pandas Series ("series") or a dictionary ("dict"). Defaults to
            "series".

    Returns: 
        pd.Series/dict: The content of the OrderedDict in its original format.
    """

    if type(frozen_argument) == tuple:

        if frozen_type == "series":

            return pd.Series(OrderedDict((x, y) for x, y in frozen_argument[0])).rename(frozen_argument[1])
            
        elif frozen_type == "dict":

            return dict(OrderedDict((x, y) for x, y in frozen_argument))

    else:

        return frozen_argument
