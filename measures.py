
import networkx as nx
import os

path_prefix = "../data/_simple/"

# The following repository should be downloaded and located at the same level as vcdim-tools
# It contains the graphs which will be used for 'real-world tests' (follow instructions to create _simple/)
# https://gitlab.inria.fr/graph/data 



# ============================== #
# BUILD GRAPH SETS

def get_all_graphs():
    # we fetch all files at depth 1 from the prefix, no more, no less
    graphs = []

    folders = os.listdir(path_prefix)
    for f_name in folders:
        full_folder = os.path.join(path_prefix, f_name)
        
        for g_name in os.listdir(full_folder):
            full_file = os.path.join(full_folder, g_name)
            
            if os.path.isfile(full_file):
                graphs.append(full_file)
    
    return graphs
graph_entire_set = get_all_graphs()


def get_file_from_pattern(pattern, files):
    for f in files:
        f_last = f.split("/")[-1]
        if f_last.count(pattern):
            return f
    print("Did not find the required pattern inside given files")


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
            example_set.append((p, get_file_from_pattern(p, graph_entire_set)))

    return example_set
# contains [(label, filename), ...]
graph_set_2024_labeled = get_example_set()



# get little graphs, for testing algorithms : sort entire_set by size
graph_sorted_set = graph_entire_set.copy()
graph_sorted_set.sort(key=os.path.getsize)



# ============================== #
# BUILD NX GRAPH

def build_graph_from_file(filename):
    G = nx.Graph()
    with open(filename, 'r') as file:
        _ = file.readline()  # header beginning with '# ...'
        edges_str = file.readlines()
        for e_str in edges_str:
            x, y = map(int, e_str.split(" "))
            G.add_edge(x, y)

    return G



# =============================== #
# COMPUTE MEASURES ON A SINGLE NX GRAPH

def compute_degen(g):
    cn = nx.core_number(g)
    degen = max(cn.values())
    return degen


def compute_diameter(g):
    # returns the exact value
    diam = nx.diameter(g, usebounds=True)  # said to be empirically linear with usebounds=True
    return diam


def compute_diameter_apx(g):
    # linear-time approximation (empirically tight)
    diam_apx = nx.algorithms.approximation.diameter(g)
    return diam_apx


def compute_kemeny_constant(g):
    kc = nx.kemeny_constant(g)
    rkc = round(kc, 2)  # sufficient in practice ?
    return rkc


def compute_densest_subgraph(g):
    # returns the density of the subgraph (only an approx)
    d, _ = nx.algorithms.approximation.densest_subgraph(g, iterations=5, method='fista')
    return d



# =============================== #
# COMPUTE & WRITE MEASURES ON A GRAPH SET

def degen_on_set(filename, graph_set):
    # TODO : rename, progress bar, more proper out file 

    with open(filename, 'w+') as degen_out:
        for g_s in graph_set:
            print(f" -- Set of {len(g_s)} graphs -- ")
            for g_name in g_s:
                path = path_prefix + g_name
                g = build_graph_from_file(path)
                degen_g = compute_degen(g)
                print(f"for {g_name}, \n   degen = {degen_g}")
                degen_out.write(f" {g_name} : \n{degen_g} \n\n")
            
            degen_out.write(" \n =================== \n ")



# =============================== #
# MAIN JOBS 

def main():

    print(f" ==== Fetched {len(graph_entire_set)} graphs in total ==== ")


    # degen_on_set("degen_on_examples.txt", graph_sets_2024)
    # degen_on_set("degen_entire_set.txt", graph_entire_set)



if __name__ == '__main__':
    main()

# TODO :
# * plots
# * seeds for random apx's
# * time functions 


