import collections
import itertools
import re
from tqdm.auto import tqdm
from functools import reduce

import numpy as np
import pandas as pd

from kgextension.endpoints import DBpedia, WikiData
from kgextension.schema_matching_helper import (get_common_prefixes,
                                                calc_string_similarity,
                                                clean_string,
                                                get_value_overlap)
from kgextension.sparql_helper import endpoint_wrapper
from kgextension.uri_helper import uri_querier


def relational_matching(
    df, endpoints=[DBpedia, WikiData], uri_data_model=False, match_score=1, progress=True, caching=True):
    """Creates a mapping of matching attributes in the schema by checking for
    owl:sameAs, owl:equivalentClass, owl:Equivalent and wdt:P1628 links between 
    them.

    Args:
        df (pd.DataFrame): Dataframe where matching attributes are supposed to 
            be found.
        endpoints (list, optional): SPARQL Endpoint to be queried. Defaults to 
            [DBpedia, WikiData].
        uri_data_model (bool, optional): If enabled, the URI is directly queried
            instead of a SPARQL endpoint. Defaults to False.
        match_score (int, optional): Score of the match: 0 < match_score <= 1. 
            Defaults to 1.
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process (if 
            "uri_data_model" = True). Defaults to True.
        caching (bool, optional): Turn result-caching for queries issued during 
            the execution on or off. Defaults to True.

    Returns:
        pd.DataFrame: Two columns with matching links and a third column with
        the score, which is always one in case of the relational matching
        unless specified otherwise.
        
    """

    matches = pd.DataFrame(columns=["uri_1", "uri_2", "value"])

    # determine attribute columns
    cat_cols = [col for col in df.columns if re.findall("http:", col)]
    cat_cols_stripped = [re.sub(r"^.*http://", "http://", col)
                         for col in cat_cols]

    if not cat_cols:
        return matches
    # transform attributes to sparql values list form
    values = "(<"+pd.Series(cat_cols_stripped).str.cat(sep=">) (<")+">) "

    if uri_data_model:
        # formulate query
        query = "PREFIX wdt: <http://www.wikidata.org/prop/direct/>"
        query += "SELECT ?value ?object WHERE {VALUES (?value) { (<**URI**>)}"
        query += " ?value\
             (owl:equivalentProperty|owl:equivalentClass|owl:sameAs|wdt:P1628)\
                  ?object. }"
        temp_df = pd.DataFrame(cat_cols_stripped, columns=["values"])
        same_cats = uri_querier(temp_df, "values", query, caching=caching, progress=progress)

        if same_cats.empty:
            return matches
        else:
            same_cats = same_cats.drop(
                same_cats[same_cats["value"] == same_cats["object"]].index)

    else:
        if not isinstance(endpoints, list):
            endpoints = [endpoints]

        same_cats = pd.DataFrame(columns=["value", "object"])

        for endpoint in endpoints:

            # formulate query
            query = "PREFIX wdt: <http://www.wikidata.org/prop/direct/>"
            query += "SELECT  ?value ?object WHERE {VALUES (?value) {" 
            query += values 
            query += "} ?value\
                 (owl:equivalentProperty|owl:equivalentClass|owl:sameAs|wdt:P1628)\
                      ?object. }"

            # query the equivalent classes/properties
            query_result = endpoint_wrapper(
                query, endpoint, caching=caching)
            if not query_result.empty:
                query_result = query_result.drop_duplicates().\
                    reset_index(drop=True)

            # group equivalent classes/properties for each original attribute
            same_cats = same_cats.append(query_result, ignore_index=True)

    if same_cats.empty:
        return matches

    combinations = list(itertools.combinations(cat_cols_stripped, 2))
    combinations_sorted = pd.DataFrame(
        [sorted(x) for x in combinations], columns=["uri_1", "uri_2"])

    # detect matches in the attributes
    for _, row in same_cats.iterrows():
        if row["object"] in cat_cols_stripped:
            # if there is a match insert it in alphabetical order into the
            # output matches dataframe
            new_match = {"uri_1": min(row["value"], row["object"]), 
                         "uri_2": max(row["value"], row["object"]), 
                         "value": match_score}
            matches = matches.append(new_match, ignore_index=True)

    matches = matches.drop_duplicates()
    full_matches = combinations_sorted.merge(
        matches, on=["uri_1", "uri_2"], how="outer")
    full_matches["value"] = np.where(
        full_matches["value"].isna(), 0, full_matches["value"])

    return full_matches


def string_similarity_matching(
    df, predicate="rdfs:label", to_lowercase=True, remove_prefixes=True, 
    remove_punctuation=True, similarity_metric="norm_levenshtein", 
    prefix_threshold=1, n=2, progress=True, caching=True):
    """Calculates the string similarity from the text field obtained by
    querying the attributes for the predicate, by default rdfs:label.

    Args:
        df (pd.DataFrame): Dataframe where matching attributes are supposed to
            be found
        predicate (str, optional):  Defaults to "rdfs:label".
        to_lowercase (bool, optional): converts queried strings to lowercase.
            Defaults to True.
        remove_prefixes (bool, optional): removes prefices of queried strings.
            Defaults to True.
        remove_punctuation (bool, optional): removes punctuation from queried
            strings. Defaults to True.
        similarity_metric (str, optional): norm by which strings are compared.
            Defaults to "norm_levenshtein".
        prefix_threshold (int, optional): The number of occurences after which
            a prefix is considered "common". defaults to 1. n (int, optional):
            parameter for n-gram and Jaccard similarities. Defaults to 2.
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True.
        caching (bool, optional): Turn result-caching for queries issued during 
            the execution on or off. Defaults to True.

    Returns:
        pd.DataFrame: Two columns with matching links and a third column with
        the string similarity score.
    """

    # Get URIs from the column names

    cat_cols = [col for col in df.columns if re.findall("https*:", col)]
    cat_cols_stripped = [re.sub(r"^.*http://", "http://", col)
                         for col in cat_cols]

    # Query these URIs for the predicate (usually the label)

    query = "SELECT ?value ?o WHERE {VALUES (?value) {(<**URI**>)} ?value "
    query += predicate +" ?o. FILTER (lang(?o) = 'en') }"

    labels = uri_querier(pd.DataFrame(cat_cols_stripped),
                         0, query, progress=progress, caching=caching).set_index("value")

    # Get common prefixes

    common_prefixes = get_common_prefixes(labels, prefix_threshold)

    # Clean the results (i.e. the labels)

    labels["o"] = labels["o"].apply(lambda x: clean_string(
        x, common_prefixes, to_lowercase, remove_prefixes, 
        remove_punctuation))

    # Create a dictionary that maps the URIs to their result (i.e. label)

    labels.reset_index(inplace=True)
    no_label = pd.DataFrame(
        {"value": 
         [x for x in cat_cols_stripped if x not in list(labels["value"])],
         "o": np.nan})
    labels = labels.append(no_label, ignore_index=True)
    labels_dict = labels.set_index("value").T.to_dict("list")
    #labels_dict = labels.to_dict(orient="index")

    # Create all unique combinations from the URIs, order them alphabetically
    # and turn them into a DataFrame

    combinations = list(itertools.combinations(labels_dict.keys(), 2))
    combinations_sorted = [sorted(x) for x in combinations]

    result = pd.DataFrame(combinations_sorted, columns=["uri_1", "uri_2"])

    # For each combination in this DataFrame, calculate the string similarity
    # of their results (i.e. labels)

    if progress:
        tqdm.pandas(desc="String Similarity Matching: Calculate String Similarities")
        result["value_string"] = result.progress_apply(lambda x: calc_string_similarity(
            x["uri_1"], x["uri_2"], labels_dict, metric=similarity_metric, n=n),
                                            axis=1)
    else:
        result["value_string"] = result.apply(lambda x: calc_string_similarity(
            x["uri_1"], x["uri_2"], labels_dict, metric=similarity_metric, n=n),
                                            axis=1)

    return result


def label_schema_matching(
    df, endpoint=DBpedia, uri_data_model=False, to_lowercase=True, remove_prefixes=True, 
    remove_punctuation=True, prefix_threshold=1, progress=True, caching=True):
    """A schema matching method by checking for attribute -- rdfs:label between 
    links.

    Args:
        df (pd.DataFrame): The dataframe where matching attributes are supposed 
            to be found.
        endpoint (Endpoint, optional): SPARQL Endpoint to be queried. Defaults 
            to DBpedia.
        uri_data_model (bool, optional): If enabled, the URI is directly 
            queried instead of a SPARQL endpoint. Defaults to False.
        to_lowercase (bool, optional): Converts queried strings to lowercase.
            Defaults to True.
        remove_prefixes (bool, optional): Removes prefices of queried strings.
            Defaults to True.
        remove_punctuation (bool, optional): Removes punctuation from queried
            strings. Defaults to True.
        prefix_threshold (int, optional): The number of occurences after which 
            a prefix is considered "common". Defaults to 1.
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process (if 
            "uri_data_model" = True). Defaults to True.
        caching (bool, optional): Turn result-caching for queries issued during 
            the execution on or off. Defaults to True.

    Returns:
        pd.DataFrame: Two columns with matching links and a third column with the overlapped label.
    """

    matches = pd.DataFrame(
        columns=["uri_1", "uri_2", "same_label"])

    # Get URIs from the column names
    cat_cols = [col for col in df.columns if re.findall("https*:", col)]
    cat_cols_stripped = [re.sub(r"^.*http://", "http://", col)
                         for col in cat_cols]

    # transform attributes to sparql values list form
    values = "(<"+pd.Series(cat_cols_stripped).str.cat(sep=">) (<")+">) "

    if uri_data_model:
        # Query these URIs for the label
        query = "SELECT ?value ?o WHERE {VALUES (?value) {(<**URI**>)} ?value rdfs:label ?o. FILTER (lang(?o) = 'en') }"
        labels = uri_querier(pd.DataFrame(cat_cols_stripped),
                             0, query, progress = progress, caching=caching).drop_duplicates().set_index("value")

    else:

        query = "SELECT ?value ?o WHERE {VALUES (?value) {" + values + \
            "} ?value rdfs:label ?o. FILTER (lang(?o) = 'en') }"

        # query the equivalent classes/properties
        labels = endpoint_wrapper(query, endpoint, caching=caching).reset_index(drop=True)

    if labels.empty:
        return matches

    # Get common prefixes

    common_prefixes = get_common_prefixes(labels, prefix_threshold)

    # Clean the results (i.e. the labels)
    labels["o"] = labels["o"].apply(lambda x: clean_string(
        x, common_prefixes, to_lowercase, remove_prefixes, remove_punctuation))

    # Create a dictionary
    if labels.index.name == "value":
        labels.reset_index(inplace=True)

    labels_dict = labels.set_index("value").T.to_dict("list")

    #check if there are no matches
    tmp = set()
    for v in labels_dict.values():
        tmp.update(v)
    if len(labels_dict) == len(tmp):
        combinations = list(itertools.combinations(cat_cols_stripped,2))
        combinations_sorted = [sorted(x) for x in combinations]

        matches = pd.DataFrame(combinations_sorted, columns=["uri_1", "uri_2"])
        matches["same_label"] = 0
        
        return matches
        
    else:
        # Combine the uris that have the same labels into a DataFrame
        new_labels_dict = collections.defaultdict(list)
        for key, values in labels_dict.items():
            for i in values:
                new_labels_dict[i].append(key)

        df_labels = pd.DataFrame(
            list(new_labels_dict.values()), columns=["uri_1", "uri_2"])
        #df_labels["same_label"] = pd.DataFrame(list(new_labels_dict.keys()))
        df_labels.dropna(inplace=True)

        # restrict the order of uris in one row
        for _, row in df_labels.iterrows():
            new_match = {"uri_1": min(row["uri_1"], row["uri_2"]), 
                         "uri_2": max(row["uri_1"], row["uri_2"]), "same_label": 1}
            matches = matches.append(new_match, ignore_index=True)

        # Get back the uris that are not quired by rdfs:label and turn df into dict
        no_label = pd.DataFrame({"value": [
                                x for x in cat_cols_stripped if x not in list(labels["value"])], "o": np.nan})
        labels = labels.append(no_label, ignore_index=True)

        full_labels_dict = labels.set_index("value").T.to_dict("list")

        # Create all unique combinations from the URIs, order them alphabetically and turn them into a DataFrame
        combinations = list(itertools.combinations(full_labels_dict.keys(), 2))
        combinations_sorted = [sorted(x) for x in combinations]

        result = pd.DataFrame(combinations_sorted, columns=["uri_1", "uri_2"])

        # merged with the non_matched combinations and drop duplicates
        for _, row in result.iterrows():
            new_match = {"uri_1": min(row["uri_1"], row["uri_2"]), 
                         "uri_2": max(row["uri_1"], row["uri_2"]), 
                         "same_label": 0}
            matches = matches.append(new_match, ignore_index=True)

        matches.drop_duplicates(
            subset=["uri_1", "uri_2"], inplace=True, ignore_index=True)

        return matches


def value_overlap_matching(df, progress=True):
    """A schema matching method by calculating the similarities of link values.

    Args:
        df (pd.DataFrame): The dataframe where matching attributes are supposed 
            to be found.
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True.

    Returns:
        pd.DataFrame: Two columns with matching links and a third column with "value_overlap".
    """

    df = df.copy()

    # get column names, strip URIs from them & create a dictionary that maps between them
    old_colnames = [col for col in df.columns if re.findall("http:", col)]

    col_name_dict = {}

    for name in old_colnames:

        col_name_dict[re.sub(r"^.*http://", "http://", name)] = name

    new_colnames = [re.sub(r"^.*http://", "http://", col)
                    for col in old_colnames]

    # Create all unique combinations from the URIs, order them alphabetically and turn them into a DataFrame
    combinations = list(itertools.combinations(new_colnames, 2))
    combinations_sorted = [sorted(x) for x in combinations]

    # transform list into sorted DataFrame
    df_combinations = pd.DataFrame(combinations_sorted, columns=["uri_1", "uri_2"])
    df_combinations.sort_values(by="uri_1")

    # For each combination in this DataFrame, calculate the similarity of their values
    if progress:
        tqdm.pandas(desc="Value Overlap Matching: Calculate Value Overlaps")
        df_combinations["value_overlap"] = df_combinations.progress_apply(lambda x: get_value_overlap(
            df, col_name_dict, x["uri_1"], x["uri_2"]), axis=1)
    else:
        df_combinations["value_overlap"] = df_combinations.apply(lambda x: get_value_overlap(
            df, col_name_dict, x["uri_1"], x["uri_2"]), axis=1)

    return df_combinations


def matching_combiner(matching_result_dfs, method="avg", columns=None, ignore_single_missings=False, weights=None, thresholds=None, merge_on=["uri_1", "uri_2"]):
    """Combines results of the schema matching functions into a single score 
    per combination of attributes.

    Args:
        matching_result_dfs (list): Results of the schema matching functions.
        method (str/method, optional): Function combining the individual 
            scores. Defaults to "avg".
        columns (list, optional): Columns of the input dataframes to take into 
            account. If none are given automatically detects them from the 
            input. Defaults to None.
        ignore_single_missings (bool, optional): If enabled, computes scores 
            even if one of the values is missing. Defaults to False.
        weights (list, optional): Weights for weighting the different scores, 
            if method = "weighted". Defaults to None.
        thresholds (float, optional): Thresholds for thresholding the different 
            scores, if method = "thresholding". Defaults to None.
        merge_on (list, optional): Names of the columns on which the DataFrames 
            in "matching_result_dfs" should be merged. Defaults to ["uri_1",
            "uri_2"].

    Raises:
        ValueError: Raised if the input of "weights" or "thresholds" is not 
            correct.

    Returns:
        pd.DataFrame: DataFrame that contains the combined matching
        score for each URI-pair.
    """

    # TODO: Add attribute to set the handling of missings.

    results_df = reduce(lambda df1, df2: pd.merge(
        df1, df2, on=merge_on), matching_result_dfs)

    if columns == None:

        columns = [x for x in list(results_df.columns) if x not in merge_on]

    if method == "max":

        results_df["result"] = results_df.apply(lambda x: np.nan if (any(pd.isna(
            x[columns])) and not ignore_single_missings) else max(x[columns]), axis=1)

    elif method == "min":

        results_df["result"] = results_df.apply(lambda x: np.nan if (any(pd.isna(
            x[columns])) and not ignore_single_missings) else min(x[columns]), axis=1)

    elif method == "avg":

        if ignore_single_missings:

            results_df["result"] = results_df.apply(
                lambda x: np.mean(x[columns]), axis=1)

        else:

            results_df["result"] = results_df.apply(
                lambda x: np.mean(list(x[columns])), axis=1)

    elif method == "weighted":

        if weights == None:

            raise ValueError(
                "Please set the weights via the 'weights' attribute.")

        elif len(weights) != len(columns):

            raise ValueError(
                "The number of weights doesn't match the number of values ("+str(len(columns))+").")

        else:

            if ignore_single_missings:

                results_df["result"] = results_df.apply(lambda x: np.nan if all(
                    pd.isna(x[columns])) else np.nansum(x[columns]*np.array(weights)), axis=1)

            else:

                results_df["result"] = results_df.apply(
                    lambda x: x[columns]@weights, axis=1)

    elif method == "thresholding":

        if thresholds == None:

            raise ValueError(
                "Please set the weights via the 'weights' attribute.")

        elif len(thresholds) != len(columns):

            raise ValueError(
                "The number of weights doesn't match the number of values ("+str(len(columns))+").")

        else:

            columns_bin = [str(x)+"_bin" for x in columns]

            for x in range(len(columns)):

                results_df[str(columns_bin[x])] = results_df[str(
                    columns[x])].ge(thresholds[x])

            results_df["result_inter"] = results_df[columns_bin].sum(axis=1)
            results_df["any_nan"] = results_df.apply(
                lambda x: any(pd.isnull(x[columns])), axis=1)
            results_df["all_nan"] = results_df.apply(
                lambda x: all(pd.isnull(x[columns])), axis=1)

            def create_final_result(result_inter, any_nan, all_nan, ignore_single_missings):

                if all_nan:
                    return np.nan

                elif any_nan and not ignore_single_missings:
                    return np.nan

                else:
                    return result_inter

            results_df["result"] = results_df.apply(lambda x: create_final_result(
                x["result_inter"], x["any_nan"], x["all_nan"], ignore_single_missings), axis=1)

    elif callable(method):

        results_df["result"] = results_df.apply(
            lambda x: method([x[columns]]), axis=1)

    return results_df[merge_on + ["result"]]
