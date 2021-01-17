import re

import networkx as nx
import numpy as np
import pandas as pd
from info_gain import info_gain
from sklearn.neighbors import NearestNeighbors
from tqdm.auto import tqdm

def add_hierarchy_columns(df, G, keep_prefix=False):
    """Given a feature dataframe and corresponding hierarchy graph, add all the
    higher-level features to the dataframe with correct boolean values.

    Args:
        df (pd.DataFrame): Dataframe with all the lowest-level children 
            features.
        G (nx.DiGraph): Directed feature hierarchy graph, direction from 
            children to parents.
        keep_prefix (bool, optional): Whether to keep prefices from original 
            directory children. Defaults to False.

    Returns:
        pd.DataFrame: Dataframe with all higher hierarchy features appended.
    """

    # determine the original lowest hierarchy level features
    leafs = [node for node in G.nodes if G.out_degree(
        node) >= 0 and G.in_degree(node) == 0]

    # strip the features of prefices not present in the graph
    df_with_hierarchy_columns = df.copy()
    if keep_prefix:
        cols_to_save = df_with_hierarchy_columns.columns.copy()
    df_with_hierarchy_columns.columns = [
        re.sub(r"^.*?http://", 
               "http://", 
               col) for col in df_with_hierarchy_columns.columns]

    # determine all higher hierachy features
    higher_hierarchy_nodes = set(G.nodes) - set(leafs)

    while bool(higher_hierarchy_nodes):
        parents_to_remove = list()

        for parent in higher_hierarchy_nodes:
            children = list(G.predecessors(parent))
            # pass the feature if it is not yet a direct parent of a feature in
            # the df
            if not set(children).issubset(set(df_with_hierarchy_columns.columns)):
                pass
            else:
                # add the parent; if any of its children has true --> True else False
                df_with_hierarchy_columns[parent] =\
                    df_with_hierarchy_columns.loc[:, children].any(axis=1).values
                parents_to_remove += [parent]

        # if parent was added remove it from the higher_hierarchy_nodes
        for parent in parents_to_remove:
            higher_hierarchy_nodes.remove(parent)

    if keep_prefix:
        no_cols_to_write_back = len(cols_to_save)
        renaming_dict = dict(
            zip(df_with_hierarchy_columns.columns[:no_cols_to_write_back], 
                cols_to_save)
        )
        df_with_hierarchy_columns.rename(columns=renaming_dict, inplace=True)

    return df_with_hierarchy_columns


def hill_climbing_cost_function(df, class_col, alpha, beta, k):
    """Calculates the regularized purity for the hierarchical hill climbing 
    algorithm using Nearest Neighbors.

    Args:
        df (pd.DataFrame): Dataframe with the feature selection to be evaluated.
        class_col (pd.Series): The column with the class/output values.
        alpha (float): Size of original feature space.
        beta (float): Regulatization parameter.
        k (int): Number of nearest neighbors.

    Returns:
        float: Cost value for this set of features.
    """

    assert (df.index == class_col.index).all()
    df_imputed = df.copy().fillna(False)

    # determine left-hand side of cost function
    n = len(df_imputed.columns)
    regularization_constant = (1 + ((alpha-n)/alpha) * beta)

    # find nearest neighbors of every data point
    nrbs = NearestNeighbors(n_neighbors=k).fit(df_imputed)
    _, indices = nrbs.kneighbors(df_imputed)

    # calculate purity (right-hand side of cost function)
    # by checking for each data point how many neareast neighbors
    # belong to the same class
    purity = 0
    for i, index in enumerate(indices):
        for ind in index:
            if class_col[ind] == class_col[i]:
                purity += 1

    # calculate cost function
    cost = regularization_constant*purity

    return cost


def exist_unchecked_leafs(G):
    """Helper function for hierachical hill climbing. The function determines
    whether any of the leaf nodes of the graph have the attribute checked set
    to False. It returns number of leafs for which this is the case.

    Args:
        G (nx.DirectedGraph): The directed graph to be checked.

    Returns:
        int: Number of unchecked leafs.
    """

    # set counter and determine leaves
    count_unchecked = 0
    leafs = [node for node in G.nodes if G.in_degree(node) == 0]

    # check all leaves and count the unchecked ones
    for leaf in leafs:
        if G.nodes[leaf]["checked"] == False:
            count_unchecked += 1
            
    # return number of unchecked leafs
    return count_unchecked


def calculate_lift(df, G, label_column):
    """Helper function for TSEL filter. Calculates the lift value for every
    node in a given graph.

    Args:
        df (pd.DataFrame): Dataframe the lift needs to be calculated for.
        G (nx.DirectedGraph): Directed graph for the dataframe.
        label_column (str): Name of the column with the class/label.

    Returns:
        dictionary: Dictionary containing column names as keys and lift as
        value.
    """

    lift_values = []

    # iterate over all nodes in hierarchy
    for node in G.nodes:
        if node != "VRN":
            
            try:
                # numeric label
                # calculate probability of attribute value being 1 or true
                attribute_probability = df[node].fillna(0).sum() / len(df)

                # calculate probability of attribute value being 1 or true and positive class label
                joint_probability = (df[node][df[label_column] > 0]).fillna(
                        0).gt(0).sum() / len(df)

            except TypeError as e:
                # nominal label
                # calculate probability of attribute value being 1 or true
                attribute_probability = df[node].fillna(0).sum() / len(df)

                # calculate probability of attribute value being 1 or true and positive class label
                joint_probability = (df[node][df[label_column] > ""]).fillna(
                        0).gt(0).sum() / len(df)
            finally:
                # calculate lift value
                lift = joint_probability / attribute_probability
                lift_values.append(lift)

    lift_value_per_node = dict(zip(G.nodes, lift_values))
    return lift_value_per_node


def get_all_paths(G, root):
    """Helper function for TSEL filter. Returns all possible paths in a given
    graph.

    Args:
        graph (nx.DirectedGraph): Directed graph.
        root (str): Name of the root node.

    Returns:
        list: List containing all paths in the graph.
    """
    # get all leafs
    leafs = [x for x in G.nodes() if G.in_degree(x) >
             0 and G.out_degree(x) == 0]
    # get all paths
    paths = []
    for leaf in leafs:
        paths = paths + (list(nx.all_simple_paths(G, root, leaf)))
    return paths


def representative_feature(path, values):
    """Helper function for TSEL filter. Returns the representative node of a
    given path.

    Args:
        path (list): Path containing some node names.
        values (dict): values containing nodes and their values.

    Returns:
        str: Name of most valuable/representative node of the given path.
    """
    max_value = -1
    rep_node = None
    for node in path:
        if node == "VRN":
            continue

        if values[node] > max_value:
            max_value = values[node]
            rep_node = node
    return rep_node


def calc_average_ig(path_nodes, node_values):
    """Helper function for SHSEL filter algorithm. It returns the average
    Infomation gain value of one existing path in pruning function.

    Args:
        path_nodes (list): Node in path whose node_availability is True.
        node_values (dict): Dictionary about every node in the directed graph
            and its information gain value.

    Returns:
        float: The average InfoGain value of one existing path.
    """

    List = []

    global average_ig

    for no in path_nodes:

        List.append(node_values[no])

    if len(path_nodes) != 0:

        average_ig = sum(List)/len(path_nodes)

    return average_ig


def find_shortest_paths(G, root="VRN", progress=True):
    """Finds the shortest path between the (virtual) root node of a grahp 
    and each leaf of the graph.

    Args:
        G (nx.DirectedGraph): Directed Graph.
        root (str, optional): Name of the root node. Defaults to "VRN".
        progress (bool, optional): If True, progress bars will be shown to inform the 
            user about the progress made by the process. Defaults to True.

    Returns:
        list: List of shortest paths.
    """

    P = []

    leaves = [x for x in G.nodes() if G.out_degree(x) ==
              0 and G.in_degree(x) > 0]

    if progress:
        iterator = tqdm(
            leaves, desc="Greedy Top Down - (1/3) Finding shortest paths.")
    else:
        iterator = leaves

    for leaf in iterator:

        P.append(nx.shortest_path(G, root, leaf))

    return P


def calc_gr(df, label_column, progress=True):
    """Calculated the Gain Ratio for each column of a df in relation to a 
    specified label_column.

    Args:
        df (pd.DataFrame): Dataframe the Gain Ratio values need to be 
            calculated for.
        label_column (str): Name of the label_column.
        progress (bool, optional): If True, progress bars will be shown to inform the 
            user about the progress made by the process. Defaults to True.

    Raises:
        RuntimeWarning: Is raised if the gain ratio calculation fails 
            for a column (and returns a nan).

    Returns:
        dict: Dictionary with the column names as keys and the corresponding
        Gain Ratio values as values.
    """

    gr_values = dict()

    if progress:
        iterator = tqdm(
            df.columns, desc="Greedy Top Down - (2/3) Calculating Gain Ratios.")
    else:
        iterator = df.columns

    for column in iterator:

        gr_values[column] = info_gain.info_gain_ratio(
            df[label_column], df[column])

        # Check if the gain ratio was successfully calculated.

        if pd.isna(gr_values[column]):

            # Check if the gain ratio was unsuccessfully calculated because all values of a column are equal (GR not defined) -> Set GR to 0.

            if len(np.unique(df[column])) == 1:

                gr_values[column] = 0

            else:

                raise RuntimeWarning(
                    "The information gain ratio of column "+column+" could not be calculated (is nan).")

    gr_values["VRN"] = 0.0

    return gr_values


def get_max_node(candidates, gr_values, column_prefix=""):
    """Given a set of candidate nodes, and return the one with the 
    highest Gain Ratio.

    Args:
        candidates (list): List of candidate nodes.
        gr_values (dict): Dictionary with column names as keys and 
            the corresponding Gain Ratio values as values.
        column_prefix (str): Prefix of the columns generated by the generator 
            (e.g. "new_link_type_"). Defaults to "".

    Returns:
        str: Name of the node with the highest Gain Ratio in the candidate set.
    """

    max_gr = 0
    max_gr_node = None

    for node in candidates:

        try:

            gr = gr_values[column_prefix+node]

        except:

            gr = gr_values[node]

        if gr > max_gr or (gr == 0 and len(candidates) == 1):

            max_gr = gr
            max_gr_node = node

    return max_gr_node


def gtd_logic(df, G, label_column, column_prefix, progress=True):
    """Greedy Top Down algorithm to select most relevant nodes in a Graph based 
    on Gain Ratio.

    Args:
        df (pd.DataFrame): DataFrame.
        G (nx.DirectedGraph): Directed Graph containing the hierarchy.
        label_column (str): Name of the label column.
        column_prefix (str): Prefix of the columns generated by the generator 
            (e.g. "new_link_type_").
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True.

    Returns:
        set: Set of nodes (as strings) that are deemed most relevant by the 
        algorithm.
    """

    # Create a collection of shortest Paths from the root node (VRN) to each of the leave nodes

    P = find_shortest_paths(G, progress=progress)

    # Calculate the Gain Ratio for each feature in the data (therby for each node in the Graph)

    gr_values = calc_gr(df, label_column, progress=progress)

    SF = set()

    # Create a dictionary to keep track of the availability of nodes

    node_availability = {}

    for node in list(G.nodes()):

        node_availability[node] = True

    if progress:
        iterator = tqdm(
            P, desc="Greedy Top Down - (3/3) Finding most relevant nodes.")
    else:
        iterator = P

    for path in iterator:

        # Get candidate_nodes for that path. Candidate Nodes are nodes that are part of the path AND are still available

        candidate_nodes = [
            node for node in path if node_availability[node] == True]

        # Check if there are any available nodes in the path.

        if len(candidate_nodes) > 0:

            # Get the Candidate Node with the highest Gain Ratio

            max_node = get_max_node(candidate_nodes, gr_values, column_prefix)

            # Add that Node to the Selected Features Set (SF)

            SF.add(max_node)

            # Change the availability of that node, it's ancestors and it's descendants to False

            node_availability[max_node] = False

            for ancestor in nx.ancestors(G, max_node):

                node_availability[ancestor] = False

            for decendant in nx.descendants(G, max_node):

                node_availability[decendant] = False

        # Check if there are any available nodes left. If not, end the algorithm.

        if all(availability == False for availability in node_availability.values()):

            break

    return SF


def prune(
    df_filtered, G, node_values, node_availability, 
    L, remove_flag=True, progress=True):
    """The pruning function of hierarchy_based_filter algorithm: select only
    the most valuable features which is greater than the average Information
    Gain values from the previously reduced set.

    Args:
        df_filtered (pd.DataFrame): The result dataframe which is outputed by
            initial selection algorithm.
        G (nx.DirectedGraph): The reverse of the directed graph of all classes
            and superclasses.
        node_values (dictionary): Dictionary contains the information gain
            value of every node in DirectedGraph.
        node_availability (dictionary): Dictionary contains every node in
            DirectedGraph and its availability (either True or False).
        L (list) : A list contains the leaf nodes in DirectedGraph.
        remove_flag (bool, optional): If or not strictly remove all the nodes 
            once one of their info gain value are smaller than the average info 
            gain of paths. Defaults to True.
        progress (bool, optional): If True, progress bars will be shown to 
            inform the user about the progress made by the process. Defaults to 
            True.

    Returns:
        pd.DataFrame: Filtered Dataframe containing the selected attributes.
    """

    # create vitual root node
    roots_and_isolated_nodes = [x for x in G.nodes(
    ) if G.out_degree(x) >= 0 and G.in_degree(x) == 0]

    for node in roots_and_isolated_nodes:

        G.add_edge("VRN", node)

    # collect all existing paths into P

    P = []

    tmp = [l for l in L if node_availability[l] == True]

    for l in tmp:

        root = "VRN"

        tmp_paths = list(nx.all_simple_paths(G, root, l))

        for path in tmp_paths:

            P.append(path)

    # start pruning by removing attrs with ig smaller than average
    node_availability["VRN"] = False

    availability_dict = {}

    if remove_flag:
        
        if progress:
            iterator = tqdm(P, desc="Hierarchy Based Filter: Pruning")
        else:
            iterator = P

        for path in iterator:

            path_nodes = [
                node for node in path if node_availability[node] == True]

            path_average_ig = calc_average_ig(path_nodes, node_values)

            for node in path_nodes:

                if node_values[node] < path_average_ig:

                    availability_dict[node] = False

        for node in availability_dict.keys():

            node_availability[node] = False

    else:

        if progress:
            iterator = tqdm(P, desc="Hierarchy Based Filter: Pruning")
        else:
            iterator = P

        for path in iterator:

            path_nodes = [
                node for node in path if node_availability[node] == True]

            path_average_ig = calc_average_ig(path_nodes, node_values)

            for node in path_nodes:

                if node in availability_dict.keys():

                    continue

                if node_values[node] >= path_average_ig:

                    availability_dict[node] = True

        node_availability = dict.fromkeys(node_availability, False)

        for node in availability_dict.keys():

            node_availability[node] = True

    SF = [node for node in list(G.nodes()) if node_availability[node] == True]

    for col in df_filtered.columns:

        if col not in SF:

            df_filtered.drop(col, axis=1, inplace=True)

    return df_filtered
