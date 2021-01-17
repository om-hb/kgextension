import pandas as pd
import numpy as np
import string as strng
import re

from collections import Counter
from fuzzywuzzy import fuzz
from strsimpy.jaccard import Jaccard
from strsimpy.ngram import NGram
from strsimpy.levenshtein import Levenshtein

def get_common_prefixes(df, threshold, column_name = "o"):
    """Finds common string prefixes (of type PREFIX:string) in a column of a
    specified DataFrame. Creates a list of all prefixes that appear more often
    than the specified threshold.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        threshold (int): The threshold to filter uncommon prefixes.
        column_name (str, optional): Column name of the column containing the 
            relevant strings. Defaults to "o".

    Returns:
        list: A list of all prefixes (of type PREFIX:string) that appear more 
        often than the specified threshold.
    """

    labels = df[column_name].dropna().tolist()

    prefixes = [label.split(":", 1)[0] for label in labels if ":" in label]

    prefixes = Counter(prefixes)

    common_prefixes = {prefix:count for (prefix,count) in prefixes.items() if count >= threshold}

    common_prefixes = list(common_prefixes.keys())

    return common_prefixes


def clean_string(string, common_prefixes, to_lowercase=True, remove_prefixes=True, remove_punctuation=True):
    """Cleans a passed string by e.g. lowercasing it, stripping common prefixes 
    from it and removing any punctuation.

    Args:
        string (str): The string that should be cleaned.
        common_prefixes (list): A list containing all (common) prefixes that 
            should be removed.
        to_lowercase (bool, optional): Indicates whether or not the string 
            should be transformed to lowercase. Defaults to True
        remove_prefixes (bool, optional): Indicates whether or not the string 
            should be stripped from the specified common prefixes (of type: 
            PREFIX:string). Defaults to True.
        remove_punctuation (bool, optional): Indicates whether or not all 
            punctuation should be removed from the string. Defaults to True.

    Returns:
        str: The cleaned string.
    """

    if pd.isna(string):

        return string

    else:

        if remove_prefixes:

            if ":" in string:

                if string.split(":", 1)[0] in common_prefixes:

                    string = string.split(":", 1)[1]

        if to_lowercase:

            string = string.lower()

        if remove_punctuation:

            regex = re.compile('[%s]' % re.escape(strng.punctuation))
            string = regex.sub('', string)

        return string


def calc_string_similarity(uri_1, uri_2, label_dict, metric="norm_levenshtein", n=2):
    """Calculates the string similarity between two strings based on various
    metrics. The strings are retreived from a dictionary provided to the
    function.

    Args:
        uri_1 (str): URI linked to the first string (used as key for the 
            label_dict).
        uri_2 (str): URI linked to the second string (used as key for the 
            label_dict).
        label_dict (dict): Dictionary mapping the provided URIs (keys) to their 
            respective strings.
        metric (str/method, optional): Name of the metric that should be used 
            for the similarity calculation. Defaults to "norm_levenshtein".
        n (int, optional): n-Value for the metrics "ngram" and "jaccard". 
            Defaults to 2.
        
    Raises:
        ValueError: Gets raised in case a unknown metric is provided.

    Returns:
        float: The similarity between the two strings.
    """

    if any(pd.isna([label_dict[uri_1], label_dict[uri_2]])):

        return np.nan

    else:

        # Used to normalize all metrics to an range of [0:1]
        divider = 1
        # Used to indicate that a distance needs to be transformed to a similarity
        distance_to_similarity = False

        if metric == "norm_levenshtein":

            function = fuzz.ratio
            divider = 100

        elif metric == "partial_levenshtein":

            function = fuzz.partial_ratio
            divider = 100

        elif metric == "token_sort_levenshtein":

            function = fuzz.token_sort_ratio
            divider = 100

        elif metric == "token_set_levenshtein":

            function = fuzz.token_set_ratio
            divider = 100

        elif metric == "ngram":
            function = NGram(n).distance
            distance_to_similarity = True

        elif metric == "jaccard":
            function = Jaccard(n).distance
            distance_to_similarity = True

        elif callable(metric):

            function = metric

        else:

            raise ValueError('Incorrect metric provided. Supported metrics are: "norm_levenshtein", "partial_levenshtein", "token_sort_levenshtein", "token_set_levenshtein", "ngram" & "jaccard". Passing a custom functions is also possible.')

        if distance_to_similarity:

            ratio = 1-(function(label_dict[uri_1], label_dict[uri_2])/divider)

        else:

            ratio = function(label_dict[uri_1], label_dict[uri_2])/divider

        return ratio


def get_value_overlap(df, col_name_dict, uri_1, uri_2):
    """Calculates the ratio of overlapping values of two columns of a 
    DataFrame, using row-wise comparison.

    Args:
        df (pd.DataFrame): The DataFrame containing the rows that should be 
            compared (with column names reduced to the URIs).
        col_name_dict (dict): Dictionary mapping the cleaned column names from 
            the DataFrame to the full column names.
        uri_1 (str): Column name of the first column (just the URI).
        uri_2 (str): Column name of the second column (just the URI).

    Returns:
        float: Ratio of overlapping values in the two columns.
    """

    equivalence = df[col_name_dict[uri_1]] == df[col_name_dict[uri_2]]

    equivalence_ratio = equivalence.sum()/len(equivalence)

    return equivalence_ratio
