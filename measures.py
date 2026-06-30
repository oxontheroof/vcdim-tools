
import networkx as nx
import bounds
import sage.all as sg

from external import vcdim_cmd
from io_data import build_graph_from_file, graphs_2023_lite_simple


# =============================== #
# COMPUTE MEASURES ON A SINGLE NX GRAPH

def n_edges(g : nx.Graph) -> int:
    return g.size()


def n_nodes(g : nx.Graph) -> int:
    return len(g)


def compute_degen(g : nx.Graph) -> int:
    cn = nx.core_number(g)
    degen = max(cn.values())
    return degen


def compute_diameter(g : nx.Graph) -> int:
    # returns the exact value
    try:
        diam = nx.diameter(g, usebounds=True)  # said to be empirically linear with usebounds=True
        return diam
    except nx.exception.NetworkXError:  # sadly happens when the graph is not connected ... 
        return -1
    

def compute_diameter_apx(g : nx.Graph) -> int:
    # linear-time approximation (empirically tight)
    try:
        diam_apx = nx.algorithms.approximation.diameter(g)
        return diam_apx
    except nx.exception.NetworkXError:
        S = [g.subgraph(c).copy() for c in nx.connected_components(g)]
        diam_apx_S = [nx.algorithms.approximation.diameter(h) for h in S]
        return max(diam_apx_S)
    

#####  TOO SLOW on as-skitter, abandonned
def compute_densest_subgraph(g : nx.Graph) -> int:
    # returns the density of the subgraph (only an approx)
    d, _ = nx.algorithms.approximation.densest_subgraph(g, iterations=5, method='fista')
    rd = round(d, 2)
    return rd


def compute_modular_width(g : nx.Graph) -> int:
    # returns the maximum degree of a node in the MDtree of G
    sgg = sg.Graph(g)
    md_tuple = sgg.modular_decomposition(style='tuple')
    return len(md_tuple[1])  # THIS IS FALSE




# TODO:MOVE
# =============================== #
# COMPUTE & WRITE MEASURES ON A GRAPH SET

def measures_on_set(graph_set, output_filename):
    print(f"Computing measures on {len(graph_set)} graphs")
    
    measures = [
        # n_nodes,
        # n_edges,
        # compute_degen,
        # compute_diameter_apx,
        # compute_densest_subgraph
        # bounds.bound_on_edges,
        # bounds.bound_on_highest_degrees
        compute_modular_width
    ]

    header = "# [graph_filename]"
    for m in measures:
        header += " [" + m.__name__ + "]"
    header += '\n'

    with open(output_filename, 'w+') as output:
        output.write(header)
        
        for g_name in graph_set:
            output_line = g_name + " "
            
            print(f"Building nx graph of {g_name} ...", end=" ", flush=True)
            g = build_graph_from_file(g_name)
            print("done.")

            for m in measures:
                print(f"{m.__name__}(g) ...", end=" ", flush=True)
                m_g = m(g)
                print(f"done ({m_g})")
                output_line += f" {m_g}"
            output_line += '\n'

            output.write(output_line)



# =============================== #
# MAIN JOBS 

def main():

    # g = graphs_small_set[0]
    # print(f"vcdim({g}) = {vcdim_cmd(g)}")
    # return



    # Manually set graph working set
    graph_set = graphs_2023_lite_simple[:20]
    print(f" ==== Fetched {len(graph_set)} graphs in total ==== ")


    default_output = "measures_output.txt"
    output_filename = input(f" Enter filename for output (Enter for default = {default_output}) : ")
    if len(output_filename) <= 0:
        output_filename = default_output
    

    measures_on_set(graph_set, output_filename)




if __name__ == '__main__':
    main()

# TODO :
# * plots
# * seeds for random apx's
# * time functions 


