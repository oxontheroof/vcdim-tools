
# Will be used to build the graphs and read data (same format)

import os
import networkx as nx

# TODO:CHANGE (select 2023 or 2024)
data2024 = ["../data/_simple/", 1]
data2023 = ["../network-corpus/networks", 0]
data2023_lite_simple = ["../network-corpus/_simple_networks/", 0]
unit_data = ["unit_data/", 0]

allowed_suffixes = ['txt', 'edgelist']

def is_comment(line):
    return (len(line) > 0 and line[0] == '#')

def remove_brackets(text):
    begin = 1 if text[0] == '[' else 0
    if text[-1] == ']':
        return text[begin:-1]
    return text[begin:]

# The following repository should be downloaded and located at the same level as vcdim-tools
# It contains the graphs which will be used for 'real-world tests' (follow instructions to create _simple/)
# https://gitlab.inria.fr/graph/data 


# ============================== #
# BUILD GRAPH SETS


def sorted_files(getter):
    def g(*args, **kwargs):
        res = getter(*args, **kwargs)
        return sorted(res)
    return g

@sorted_files
def get_all_graphs(base, depth):
    # we fetch all files at some depth from the prefix with some allowed suffix
    graphs = []

    if depth <= 0:
        for g_name in os.listdir(base):
            file = os.path.join(base, g_name)
            suffix = file.split('.')[-1]
            if os.path.isfile(file) and suffix in allowed_suffixes:
                graphs.append(file)

        return graphs

    folders = os.listdir(base)
    for f_name in folders:
        folder = os.path.join(base, f_name)
        graphs.extend(get_all_graphs(folder, depth - 1))
    
    return graphs


def get_file_from_pattern(pattern, files):
    for f in files:
        f_last = f.split("/")[-1]
        if f_last.count(pattern):
            return f
    print("Did not find the required pattern inside given files")



# =========================== #
# SOME GRAPHS SETS

graphs_2024 = get_all_graphs(*data2024)
graphs_2023 = get_all_graphs(*data2023)
graphs_2023_lite_simple = get_all_graphs(*data2023_lite_simple)
graphs_unit = get_all_graphs(*unit_data)

# set of graphs used in COATI24 experiments --- repartition in distinct sets
def get_example_set():

    categories = {
        '1_bio' : [
            "BIOGRID-MV-Physical-3.5.169",
            "BIOGRID-SYSTEM-Affinity_Capture-MS-3.5.169",
            "BIOGRID-SYSTEM-Affinity_Capture-RNA-3.5.169",
            "dip20170205"
        ],
        '2_autonomous_internet' : [
            "oregon2_010331",
            "CAIDA_as_20130601",
            "DIMES_201204"
        ],
        '3_computer_networks' : [
            "as-skitter",
            "p2p-Gnutella09",
            "gnutella31-d"
        ],
        '4_web' : [
            "notreDame-d",
            "y-BerkStan-d"
        ],
        '5_coauthors' : [
            "ca-HepPh",
            "com-dblp.ungraph"
        ],
        '6_social_networks' : [
            "epinions1-d",
            "facebook_combined",
            "twitter_combined-d"
        ],
        '7_road_networks' : [
            "t.CAL-w",
            "t.FLA-w"
        ],
        '8_others' : [
            "buddha-w",
            "froz-w",
            "z-alue7065"
        ]
    }

    cat_order = sorted(categories.keys())

    example_set = []
    for c in cat_order:
        for p in categories[c]:
            example_set.append((p, get_file_from_pattern(p, graphs_2024)))

    return example_set

# contains [(label, filename), ...]
graphs_examples_2024_labeled = get_example_set()

graphs_examples_2024 = [g for _, g in graphs_examples_2024_labeled]  # forget label

# get little graphs, for testing algorithms : sort entire_set by size
graphs_2024_sorted = graphs_2024.copy()
graphs_2024_sorted.sort(key=os.path.getsize)
graphs_small_set = graphs_2024_sorted[:5]  # for fast tests



# ============================== #
# BUILD NX GRAPH

def build_graph_from_file(filename):
    G = nx.Graph()
    with open(filename, 'r') as file:
        edges_str = file.readlines()
        for e_str in edges_str:
            if e_str[0] != '#':  # skip comments (usually only one line at the beginning)
                x, y = map(int, e_str.split(" "))
                G.add_edge(x, y)

    return G


# ============================== #
# LOG - DICT CONVERSION

def log_to_dict(filename, unbrackets=True):
    """ produces a dictionnary based on a file containing
    - a header on the first line, with n distinct columns '# [col1] [col2] ...'
    - on the next lines, n elements separated by spaces """

    data = {}

    with open(filename, 'r') as file:
        header = file.readline().split(' ')[1:]
        if unbrackets:
            header = map(remove_brackets, header)

        for line in file.readlines():
            if is_comment(line):
                continue

            values = line.split(' ')
            attributes = {hi : float(vi) for (hi, vi) in zip(header[1:], values[1:])}
            data[values[0]] = attributes

    return data


