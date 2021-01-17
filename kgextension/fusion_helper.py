import warnings
from collections import Counter
import re
import random
import numpy as np

def first(x):
    """Returns the first not-NA value, helper function for pd.DataFrame.apply.

    Args:
        x (pd.Series): columns/rows passed in pd.DataFrame.apply function

    Returns:
        flexible: first not-NA value of the pd.Series
    """
    x = x.dropna()
    if x.empty:
        return np.nan
    else:
        return x[0]

def last(x):
    """Returns the last not.na value, helper function for pd.DataFrame.apply.

    Args:
        x (pd.Series): columns/rows passed in pd.DataFrame.apply function

    Returns:
        flexible: last not-NA value of the pd.Series
    """
    x = x.dropna()
    if x.empty:
        return np.nan
    else:
        return x[-1]

def longest(x):
    """Returns the longest value, helper function for pd.DataFrame.apply.

    Args:
        x (pd.Series): columns/rows passed in pd.DataFrame.apply function

    Returns:
        str: longest value of the pd.Series
    """
    x = x.dropna()
    if x.empty:
        return np.nan
    else:
        return max(x, key=len)

def shortest(x):
    """Returns the shorest value, helper function for pd.DataFrame.apply.

    Args:
        x (pd.Series): columns/rows passed in pd.DataFrame.apply function

    Returns:
        str: longest value of the pd.Series
    """
    x = x.dropna()
    if x.empty:
        return np.nan
    else:
        return min(x, key=len)

def voting(x):
    """Chooses the value with the most votes (mode value in statistics). If 
    there is a draw, the first value is chosen.

    Args:
        x (pd.Series): columns/rows passed in pd.DataFrame.apply function

    Returns:
        flexible: mode value of the pd.Series
    """

    x = x.dropna()
    if x.empty:
        return np.nan
    else:
        # count the votes
        votes = Counter(x).values()
        items = [value for value in votes]

        # warn if no winning vote can be obtained
        if max(votes) == 1:
            warnings.warn(
                "Every vote is distinct. The first value will be chosen.")

        # warn if there is a draw
        elif all(y == items[0] for y in list(items)):
            warnings.warn(
                "There is a draw in votes. The value of the first voting\
                    group/column will be chosen.")

        return max(x, key=Counter(x).get)


def provenance(columns, regex="http://dbpedia.org/"):
    """Determines the name of the column matching the regex pattern. 

    Args:
        columns (pd.DataFrame.columns): The columns of the schema matches to be
            fused
        regex (str, optional): The regex string identifiying the column name,
            generally the prefix of the feature. Defaults to 
            "http://dbpedia.org/".


    Returns:
        str: The name of the column matching the regex pattern.

    Raises:
        AttributeError: If no column or more than one columns of the fusion
            cluster match the pattern.
    """

    # identify all matches satisfying the regex pattern
    columns = columns.dropna()
    matches = [col for col in columns if re.findall(regex, col)]

    # if the match is unique, return it
    if len(matches) == 1:
        return matches[0]

    # if there are more than one or no occurences raise the respective errors
    elif len(matches) > 1:
        raise RuntimeError("""More than one of the matches satistifies the 
                           provenance regex, please specify another
                           regex or another fusion method.""")
    else:
        raise RuntimeError(""""No column satisfies the regex. Please specify 
                           another regex or another fusion method.""")

def fusion_function_lookup(
    boolean_method_single, boolean_method_multiple, numeric_method_single, 
    numeric_method_multiple, string_method_single, string_method_multiple):
    """Maps the right function to method passed as string. E.g.
    boolean_method_single = 'random' --> random.choice.

    Args:
        boolean_method_single (str): method to use for a cluster of size two
            and boolean values.
        boolean_method_multiple (str): method to use for a cluster of more than
            size two and boolean values.
        numeric_method_single (str): method to use for a cluster of size two
            and numeric values
        numeric_method_multiple (str): method to use for a cluster of more than
            size two and numeric values.
        string_method_single (str): method to use for a cluster of size two
            and string values.
        string_method_multiple (str): method to use for a cluster of more than 
            size two and string values.

    Returns:
        dict: A dictionary with the mapping from method to function.
    """
    
    # boolean functions single match: match choices and functions
    boolean_choices_single = [
        boolean_method_single == "first", boolean_method_single == "last",
        boolean_method_single == "random", boolean_method_single == "provenance",
        callable(boolean_method_single)]
    boolean_functions_single = [
        first, last, random.choice, provenance, boolean_method_single]
    boolean_function_single = np.select(
        boolean_choices_single, boolean_functions_single, default=None).item()

    # boolean functions multiple matches: match choices and functions
    boolean_choices_multiple = [
        boolean_method_multiple == "first", boolean_method_multiple == "last",
        boolean_method_multiple == "random", boolean_method_multiple == "provenance",
        boolean_method_multiple == "voting", callable(boolean_method_multiple)]
    boolean_functions_multiple = [
        first, last, random.choice, provenance,  voting, boolean_method_multiple]
    boolean_function_multiple = np.select(
        boolean_choices_multiple, boolean_functions_multiple, default=None).item()

    # numeric functions single match: match choices and functions
    numeric_choices_single = [
        numeric_method_single == "min", numeric_method_single == "max",
        numeric_method_single == "average", numeric_method_single == "random",
        numeric_method_single == "provenance", callable(numeric_method_single)]
    numeric_functions_single = [
        np.min, np.max, np.mean, random.choice, provenance, numeric_method_single]
    numeric_function_single = np.select(
        numeric_choices_single, numeric_functions_single, default=None).item()

    # numeric functions multiple matches: match choices and functions
    numeric_choices_multiple = [
        numeric_method_multiple == "min", numeric_method_multiple == "max",
        numeric_method_multiple == "average", numeric_method_multiple == "median",
        numeric_method_multiple == "random", numeric_method_multiple == "provenance",
        numeric_method_multiple == "voting", callable(numeric_method_multiple)]
    numeric_functions_multiple = [
        np.min, np.max, np.mean, np.median, random.choice, provenance, voting, 
        numeric_method_multiple]
    numeric_function_multiple = np.select(
        numeric_choices_multiple, numeric_functions_multiple, default=None).item()

    # string functions single match: match choices and functions
    string_choices_single = [
        string_method_single == "first", string_method_single == "last",
        string_method_single == "longest", string_method_single == "shortest",
        string_method_single == "random", string_method_single == "provenance",
        callable(string_method_single)]
    string_functions_single = [
        first, last, longest, shortest, random.choice, provenance, string_method_single]
    string_function_single = np.select(
        string_choices_single, string_functions_single, default=None).item()

    # string functions multiple matches: match choices and functions
    string_choices_multiple = [
        string_method_multiple == "first", string_method_multiple == "last",
        string_method_multiple == "longest", string_method_multiple == "shortest",
        string_method_multiple == "random", string_method_multiple == "provenance",
        string_method_multiple == "voting", callable(string_method_multiple)]
    string_functions_multiple = [
        first, last, longest, shortest, random.choice, provenance, voting, 
        string_method_multiple]
    string_function_multiple = np.select(
        string_choices_multiple, string_functions_multiple, default=None).item()

    # create lookup to choose function from once data type and group size are known
    function_lookup = {"boolean_single": boolean_function_single,
                       "boolean_multiple": boolean_function_multiple,
                       "numeric_single": numeric_function_single,
                       "numeric_multiple": numeric_function_multiple,
                       "string_single": string_function_single,
                       "string_multiple": string_function_multiple}
    
    return function_lookup
    