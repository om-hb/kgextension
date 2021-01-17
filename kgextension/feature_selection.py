import re

import networkx as nx
import numpy as np
import pandas as pd
from info_gain import info_gain
from tqdm.auto import tqdm

from kgextension.feature_selection_helper import (add_hierarchy_columns,
                                                  calculate_lift,
                                                  exist_unchecked_leafs,
                                                  get_all_paths, gtd_logic,
                                                  hill_climbing_cost_function,
                                                  prune,
                                                  representative_feature)


def hill_climbing_filter(
    df, label_column, metric='hill_climbing_cost_function', G=None, beta=0.05, 
    k=5, progress=True, **kwargs):
    """Feature selection performed by comparing nodes with their parents in a
    bottom-up approach.

       Wang, B.B., Mckay, R.B., Abbass, H.A. and Barlow, M., 2003, February. A
       comparative study for domain ontology guided feature extraction. In
       Proceedings of the 26th Australasian computer science conference-Volume
       16 (pp. 69-78).

    Args:
        df (pd.DataFrame): Dataframe containing the original features and the
            class column.
        label_column (str): Name of the output/class column.
        metric (str/func, optional): Cost function to determine value of    
            feature set. Higher values indicate a better feature set. Should 
            take at least df and class_col(pd.Series of class column) as input 
            and output a single numeric value. Defaults to 
            'hill_climbing_cost_function'.
        G (nx.DirectedGraph, optional): The directed graph of all classes and
            superclasses can be specified here; if None the function looks for 
            the graph in the pd.DataFrame.attrs.hierarchy attribute of the 
            input dataframe. Defaults to None.
        beta (float, optional): Regularization parameter of cost function. 
            Defaults to 0.05.
        k (int, optional): Number of nearest neighbors for cost function. 
            Defaults to 5.
        progress (bool, optional): If True, progress updates will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True. 

    Returns:
        pd.DataFrame: dataframe with filtered classes
    """
    
    df = df.copy()
    # check whether graph was given. If not, get it from the dataframe attachment 
    if G:
        G = G.copy()
    elif not df.attrs:
        raise RuntimeError("""No hierarchy graph found. It should either be
                              attached to the dataframe in df.attrs['hierarchy]
                              or passed in the G argument.""")
    else:     
        G = df.attrs["hierarchy"].copy()

    # delete and save prefix strings, e.g. 'uri_bool_" to comply with graph
    prefix_cols = [col for col in df.columns if re.findall("http:", col)]
    prefix_cols_stripped = [
        re.sub(r"^.*?http://", "http://", col) for col in prefix_cols]
    renaming_dict = dict(zip(prefix_cols_stripped, prefix_cols))
    df.columns = [re.sub(r"^.*?http://", "http://", col) for col in df.columns]

    # save class col and columns without features for later
    label_column = re.sub(r"^.*?http://", "http://", label_column)
    class_col = df.loc[:,label_column]
    non_class_cols = list(set(df.columns) - set(G.nodes) - set([label_column]))

    # initialize the leaves (initial feature set), alpha and the full dataframe
    # with columns from all hierarchy levels

    if progress:
        print("Hill Climbing Filter - (1/3) Initialization.")

    leafs = [node for node in G.nodes if G.in_degree(node) == 0]
    alpha = len(leafs)
    full_df = add_hierarchy_columns(df, G, keep_prefix=False)

    df = df.loc[:, leafs]

    # set the checked status of features in the graph
    checked = False
    nx.set_node_attributes(G, checked, "checked")

    # calculate the cost of the initial feature set

    if progress:
        print("Hill Climbing Filter - (2/3) Calculate Metric.")

    if callable(metric):
        f_curr = metric(df, class_col, **kwargs)
    else:
        f_curr = hill_climbing_cost_function(
            df, class_col, alpha=alpha, beta=beta, k=k)

    if progress:
        print("Hill Climbing Filter - (3/3) Check Leafs.")

    # do as long as there are unchecked leaves:
    while exist_unchecked_leafs(G) > 0:

        G = G.copy()

        for node in leafs:
            if node not in leafs:  
                # since could have been removed already as "sibling"
                pass

            elif G.nodes[node]["checked"] == False:

                # identify parents aka superclasses of leave node
                parents = list(G.successors(node))

                # initialise list for cost values of feature set with parents
                f_test_list = np.zeros(len(parents))

                for i, parent in enumerate(parents):

                    # identify all children of this parent node
                    children_of_parent = list(G.predecessors(parent))
                    # create alternative feature set with this parent
                    features = leafs.copy() + [parent]
                    features = [
                        col for col in features if col not in children_of_parent]

                    # create the alternative data with this feature set
                    df_to_test = full_df.loc[:, features]

                    # compute the cost of this alternative feature set
                    if callable(metric):
                        f_test_list[i] = metric(df, class_col, **kwargs)
                    else:
                        f_test_list[i] = hill_climbing_cost_function(
                            df_to_test, class_col, alpha, beta=beta, k=k)

                # if any cost value of a parent is bigger than the current cost 
                # value update the feature set
                if (f_curr < f_test_list).any():

                    # determine the parent with the highest cost value
                    successful_parent_index = np.argmax(f_test_list)
                    successful_parent = parents[successful_parent_index]
                    f_test = f_test_list[successful_parent_index]

                    # add parent and remove its children to the feature set
                    children_of_parent = list(G.predecessors(
                        parents[successful_parent_index]))
                    features = leafs.copy() + [successful_parent]
                    features = [
                        col for col in features if col not in children_of_parent]

                    # update dataset and cost value to version with superclass
                    df = full_df.loc[:, features]
                    f_curr = f_test

                    # remove all children of the newly added superclass from the graph
                    for child in children_of_parent:
                        G.remove_node(child)

                    # update the leaf node list
                    leafs = [
                        node for node in G.nodes if G.in_degree(node) == 0]

                else:
                    # mark leaf node as checked
                    G.nodes[node]["checked"] = True

    # create the final filtered dataframe
    filtered_leaves = [node for node in G.nodes if G.in_degree(node) == 0]
    if label_column in filtered_leaves:
        filtered_leaves.remove(label_column)
    filtered_df = full_df.loc[:, non_class_cols +
                              [label_column] + filtered_leaves]
    filtered_df.columns = non_class_cols + [label_column] + filtered_leaves
    filtered_df.rename(columns=renaming_dict, inplace=True)

    return filtered_df


def tree_based_filter(df, label_column, G=None, metric="Lift", progress=True):
    """Filter attributes with Tree-Based Feature Selection (TSEL). TSEL selects
    the most valuable attributes from each path in the hierarchy, based on lift
    or information gain.

        Jeong, Y. and Myaeng, S.H., 2013, October. Feature selection using a
        semantic hierarchy for event recognition and type classification. In
        Proceedings of the Sixth International Joint Conference on Natural
        Language Processing (pp. 136-144).

    Args:
        df (pd.DataFrame): Dataframe with hierarchy (output of generator)
        label_column (str): Name of the column with the class/label
        G (nx.DirectedGraph, optional): The directed graph of all classes and 
            superclasses can be specified here; if None the function looks for 
            the graph in the pd.DataFrame.attrs.hierarchy attribute of the input
            dataframe. Defaults to None.
        metric (str/func, optional): Metric which is used to determine the 
            representative features (IG/Lift). Defaults to 'Lift'.
        progress (bool, optional): If True, progress updates will be shown to   
            inform the user about the progress made by the process. Defaults to 
            True. 

    Returns:
        pd.DataFrame: Filtered Dataframe containing the selected attributes.
    """
    df = df.copy()

    if G:
        G = G.copy()
    else:
        G = df.attrs["hierarchy"].copy()

    if progress:
        print("Tree Based Filter - (1/4) Initialization.")
    
    # delete and save prefix strings, e.g. 'uri_bool_" to comply with graph
    prefix_cols = [col for col in df.columns if re.findall("http:", col)]
    prefix_cols_stripped = [
        re.sub(r"^.*?http://", "http://", col) for col in prefix_cols]
    renaming_dict = dict(zip(prefix_cols_stripped, prefix_cols))
    df.columns = [re.sub(r"^.*?http://", "http://", col) for col in df.columns]
    
    # save class col and columns without features for later
    label_column = re.sub(r"^.*?http://", "http://", label_column)
    non_class_cols = list(set(df.columns) - set(G.nodes) - set([label_column]))

    df_from_hierarchy = add_hierarchy_columns(df, G, keep_prefix=False)

    # tsel is a top-down algorithm ==> graph has to be reversed
    G = G.reverse()

    # add virtual root node
    roots_and_isolated_nodes = [x for x in G.nodes(
    ) if G.out_degree(x) >= 0 and G.in_degree(x) == 0]
    for node in roots_and_isolated_nodes:
        G.add_edge("VRN", node)

    if progress:
        print("Tree Based Filter - (2/4) Calculate Metric Values.")
        
    if callable(metric):
        node_metrics = metric(df_from_hierarchy, G, label_column)
    
    elif metric == "IG":
        metrics = []
        for node in G.nodes:
            if node != "VRN":

                ig = info_gain.info_gain(
                    df_from_hierarchy[label_column], df_from_hierarchy[node])

                metrics.append(ig)
        node_metrics = dict(zip(G.nodes, metrics))
        
    else:
        node_metrics = calculate_lift(
            df_from_hierarchy, G, label_column)

    representative_features = []

    # traverse all paths

    if progress:
        print("Tree Based Filter - (3/4) Get initial representative features.")

    for p in get_all_paths(G, "VRN"):
        # select representative feature
        feature = representative_feature(p, node_metrics)

        if feature not in representative_features:
            representative_features.append(feature)

    if progress:
        print("Tree Based Filter - (4/4) Update representative features.")

    # loop over representative features
    checkUpdated = True
    while checkUpdated == True:
        checkUpdated = False

        for feature in representative_features:

            # loop over all descendants
            for desc in nx.descendants(G, feature):

                # check if descendant is representative feature
                if desc in representative_features:
                    representative_features.remove(feature)

                    # loop over all direct child nodes of x
                    for child in nx.neighbors(G, feature):

                        # loop over all paths from child to leaf nodes
                        for p in get_all_paths(G, child):

                            # select representative feature
                            feature = representative_feature(p, node_metrics)
                            if feature not in representative_features:
                                representative_features.append(feature)

                    checkUpdated = True
                    break
            # loop again if representative nodes were updated
            if checkUpdated == True:
                break

    if label_column in representative_features:
        representative_features.remove(label_column)
        
    df_filtered = df_from_hierarchy.loc[:, non_class_cols +
                              [label_column] + representative_features]

    df_filtered.columns = non_class_cols + [label_column] + representative_features
    df_filtered.rename(columns=renaming_dict, inplace=True)

    return df_filtered


def hierarchy_based_filter(
    df, label_column, G=None, threshold=0.99, metric="info_gain", 
    pruning=True, all_remove=True, progress=True, **kwargs):
    """Feature selection approach, namely, SHSEL including the initial
    selection algorithm and pruning algorithm. Identify and filter out the
    ranges of nodes with similar relevance in each branch of the hierarchy.

        Ristoski, P. and Paulheim, H., 2014, October. Feature selection in 
        hierarchical feature spaces. In International conference on discovery 
        science (pp. 288-300). Springer, Cham.
    
    Args:
        df (pd.DataFrame): Dataframe containing the original features and the
            class column.
        label_column (str): Name of the output/class column.
        G (nx.DirectedGraph, optional): The directed graph of all classes and
            superclasses can be specified here; if None the function looks for 
            the graph in the pd.DataFrame.attrs.hierarchy attribute of the 
            input dataframe. Defaults to None.
        threshold (float, optional): A relevance similarity threshold which is 
            set be users, recommended to be 0.99. Defaults to 0.99. 
        metric (str/func, optional): The relevance similarity metrics including 
            infomation gain and correlation("info_gain"/"correlation"). Can use
            your own metric function. Defaults to "info_gain". 
        pruning (bool, optional): If or not use the pruning algorithm, if True, 
            select only the most valuable features which is greater than the 
            average Information Gain values from the previously reduced set. 
            Defaults to True.
        all_remove (bool, optional): Only valid when pruning is True. If or not 
            strictly remove all the nodes once one of their info gain value are 
            smaller than the average info gain of paths. Defaults to True.
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True.

    Returns:
        pd.DataFrame: Filtered Dataframe containing the selected attributes.
    """

    # Take graph attached to df or selected by user.
    if G == None:
        G = df.attrs["hierarchy"].copy()
        
    elif G:
        G = G.copy()
        
    else:
        raise RuntimeError("""No hierarchy graph found. It should either be
                              attached to the dataframe in df.attrs['hierarchy]
                              or passed in the G argument.""")
        
    df = df.copy()
    # delete and save prefix strings, e.g. "uri_bool_" to comply with graph
    prefix_cols = [col for col in df.columns if re.findall("http:", col)]

    prefix_cols_stripped = [
        re.sub(r"^.*?http://", "http://", col) for col in prefix_cols]

    renaming_dict = dict(zip(prefix_cols_stripped, prefix_cols))

    # preparing part
    df.columns = [re.sub(r"^.*?http://", "http://", col) for col in df.columns]

    # save class col and columns without features for later
    label_column = re.sub(r"^.*?http://", "http://", label_column)
    non_class_cols = list(set(df.columns) - set(G.nodes) - set([label_column]))
    
    class_col = df.loc[:,label_column]
    non_class_df = df.loc[:, non_class_cols]
   
    #main part
    df_from_hierarchy = add_hierarchy_columns(df, G, keep_prefix=False)

    G = G.reverse()

    if not nx.is_directed_acyclic_graph(G):

        raise TypeError(
            "The Hierarchy Based Filter is designed for directed acyclic graphs (DAGs).")

    node_availability = {}

    ig_values = []
    
    if progress:
        iterator = tqdm(list(G.nodes()), desc="Hierarchy Based Filter: Initial Selection")
    else:
        iterator = list(G.nodes())

    #for node in list(G.nodes()):
    for node in iterator:

        node_availability[node] = True

        ig = info_gain.info_gain(
            df_from_hierarchy[label_column], df_from_hierarchy[node])

        ig_values.append(ig)
        
        #global node_values

        node_values = dict(zip(G.nodes, ig_values))

    # the main structure of Inital Selection

    L = [x for x in G.nodes() if G.out_degree(x) == 0 and G.in_degree(x) > 0]

    for l in L:

        D = G.predecessors(l)   # direct ancestors of the current leaf l

        D = list(D)   # necessary! transform keydict_iterator type to list

        # selection by similarity
        for d in D:

            if callable(metric):
                
                similarity = metric(df_from_hierarchy, l, d, **kwargs) 
                
            elif metric == "info_gain":

                similarity = 1-abs(node_values[d]-node_values[l])

            elif metric == "correlation":

                similarity = np.corrcoef(
                    df_from_hierarchy[l], df_from_hierarchy[d])[0, 1]

            if similarity >= threshold or np.isnan(similarity) == True:

                node_availability[l] = False

                break

        # extend L by D

        newleaf = [d for d in D if d not in L]

        L.extend(newleaf)

    SF = [node for node in list(G.nodes()) if node_availability[node] == True]

    df_filtered = df_from_hierarchy.copy()

    for col in df_from_hierarchy.columns:

        if col not in SF or col not in df.columns:

            df_filtered.drop(col, axis=1, inplace=True)

    if pruning:

        df_filtered = prune(df_filtered, G, node_values, node_availability, 
                            L, remove_flag=all_remove, progress=progress)
    
    df_filtered = pd.concat([non_class_df, class_col, df_filtered], axis=1)

    df_filtered.rename(columns=renaming_dict, inplace=True)

    return df_filtered


def greedy_top_down_filter(df, label_column, column_prefix = "new_link_type_", G=None, progress=True):
    """Hierarchical feature selection based on the Greedy Top Down algorithm. 

        Lu, S., Ye, Y., Tsui, R., Su, H., Rexit, R., Wesaratchakit, S., Liu, X.
        and Hwa, R., 2013, October. Domain ontology-based feature reduction for
        high dimensional drug data and its application to 30-day heart failure
        readmission prediction. In 9th IEEE International Conference on
        Collaborative Computing: Networking, Applications and Worksharing (pp.
        478-484). IEEE.
    
    Args:
        df (pd.DataFrame): DataFrame that contains the label as well as the 
            features generated (by a generator).
        label_column (str): Name of the label column.
        column_prefix (str): Prefix of the columns generated by the generator 
            (e.g. "new_link_type_"). Defaults to "new_link_type_". #TODO: Check if default makes sense!
        G (nx.DirectedGraph, optional): Graph that contains the hierarchy. If 
            "None" that hierarchy attached to the provided df will be used. 
            Defaults to None.
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True.

    Raises:
        TypeError: Raised if the graph provided is not a directed acyclic graph 
            (DAGs).

    Returns:
        pd.DataFrame: DataFrame reduced to columns determined by the GTD
        algorithm as well as columns in the original df that are not created by
        a generator (that don't start with column_prefix).
    """

    # Take graph attached to df or selected by user.

    if G == None:
        G = df.attrs["hierarchy"].copy()
    else:
        G = G.copy()

    if nx.is_directed_acyclic_graph(G):

        df = df.copy()

        # Get columns in the df that are not created by a generator (that don't start with column_prefix).

        unrelated_cols = [
            col for col in df if not col.startswith(column_prefix)]

        # Add additional classes found in the hierarchy as feature columns.

        df = add_hierarchy_columns(df, G, keep_prefix=True)

        # Reverse the graph and add common root.

        G = G.reverse()

        roots_and_isolated_nodes = [x for x in G.nodes(
        ) if G.out_degree(x) >= 0 and G.in_degree(x) == 0]

        for node in roots_and_isolated_nodes:

            G.add_edge("VRN", node)

        # Run GTD algorithm to determine set of nodes to keep.

        relevant_nodes = gtd_logic(
            df, G, label_column, column_prefix, progress)

        # Remove all nodes that are not in the set of relevant_nodes NOR in the set of unrelated_cols.

        df_filtered = df.copy()

        for col in df.columns:

            if re.sub(column_prefix, '', col) not in relevant_nodes and col not in unrelated_cols:

                df_filtered.drop(col, axis=1, inplace=True)

        return df_filtered

    else:

        raise TypeError(
            "The GTD Algorithm is designed for directed acyclic graphs (DAGs).")
