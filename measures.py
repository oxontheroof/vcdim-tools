
import networkx as nx

# The following repository should be downloaded and located at the same level that this one :
# https://gitlab.inria.fr/graph/data 



# set of graphs used in COATI24 experiments --- repartition in distinct sets
graph_set_bio = [
    "sources_graphs/BIOGRID-MV-Physical-3.5.169.edgelist",
    "sources_graphs/BIOGRID-SYSTEM-Affinity_Capture-MS-3.5.169.edgelist",
    "sources_graphs/BIOGRID-SYSTEM-Affinity_Capture-RNA-3.5.169.edgelist",
    "sources_graphs/dip20170205.edgelist"
]

graph_set_autonomous_internet = [
    "snap/oregon2_010331.txt",
    "sources_graphs/CAIDA_as_20130601.edgelist",
    "sources_graphs/DIMES_201204.edgelist"
]

graph_set_computer_networks = [
    "snap/as-skitter.txt",
    "sources_graphs/p2p-Gnutella09.edgelist",
    "massive/gnutella31-d.txt"
]

graph_set_web = [
    "massive/notreDame-d.txt",
    "massive/y-BerkStan-d.txt"
]

graph_set_coauthors = [
    "sources_graphs/ca-HepPh.edgelist",
    "snap/com-dblp.ungraph.txt"
]

graph_set_social_networks = [
    "massive/epinions1-d.txt",
    "snap/facebook_combined.txt",
    "massive/twitter_combined-d.txt"
]

graph_set_road_networks = [
    "massive/t.CAL-w.txt",
    "massive/t.FLA-w.txt"
]

graph_set_others = [
    "massive/buddha-w.txt",
    "massive/froz-w.txt",
    "massive/z-alue7065.txt"
]

graph_sets_2024 = [
    graph_set_bio, 
    graph_set_autonomous_internet, 
    graph_set_computer_networks, 
    graph_set_web, 
    graph_set_coauthors, 
    graph_set_social_networks,
    graph_set_road_networks,
    graph_set_others]


def build_graph_from_file(filename):
    G = nx.Graph()
    with open(filename, 'r') as file:
        _ = file.readline()  # header beginning with '# ...'
        edges_str = file.readlines()
        for e_str in edges_str:
            x, y = map(int, e_str.split(" "))
            G.add_edge(x, y)

    return G


def compute_degen(g):
    cn = nx.core_number(g)
    degen = max(cn.values())
    return degen


def main():
    path_prefix = "../data/_simple/"

    with open("degen_on_examples.txt", 'w+') as degen_out:
        for g_s in graph_sets_2024:
            print(f" -- Set of {len(g_s)} graphs -- ")
            for g_name in g_s:
                path = path_prefix + g_name
                g = build_graph_from_file(path)
                degen_g = compute_degen(g)
                print(f"for {g_name}, \n   degen = {degen_g}")
                degen_out.write(f" {g_name} : \n{degen_g} \n\n")
            
            degen_out.write(" \n ------------------- \n ")



if __name__ == '__main__':
    main()

