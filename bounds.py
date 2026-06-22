
from math import log2
import networkx as nx
from io_data import unit_data, build_graph_from_file # graph_set_small 
# from typing import List


# Some quick things to compute other bounds


# 1. on the number of edges :
# if S is shattered, s \in S has degree >= 2^{|S| - 1} - 1.
# We may have counted some edges twice between elements of S : 
# |S| * (2^{|S| - 1} - 1) - (|S| choose 2) <= |E|
# 
# Note : this bound is cleaner and clearer with open neighbourhoods:
# |S| * 2^{S - 1} <= |E|
# 
# 
# In fact, this bound can be made even more accurate, considering the effective degree sequence (see below)

def fact(n):
    if n <= 0:
        return 1
    return n * fact(n - 1)


def binom(n, k):
    return (fact(n) // (fact(k) * fact(n - k)))


def bound_on_edges(g : nx.Graph, closed=False) -> int:
    n_edges = sum(d for _, d in g.degree()) // 2
    
    def f_open(s): 
        return s * 2**(s - 1)

    def f_closed(s):
        return s * (2**(s - 1) - 1) - binom(s, 2)

    f = f_closed if closed else f_open

    lb = 0
    ub = int(log2(n_edges)) + 1  
    # invariant : lb <= res < ub

    while ub > lb + 1:
        m = (ub + lb) // 2
        if f(m) > n_edges:
            ub = m
        else:
            lb = m

    return lb  # actually the 'upper bound' for |S| ... 

# TODO : add bound with nodes ...

def bound_on_highest_degrees(g : nx.Graph) -> int:
    """ if g has a shattered set of size s, then there are s vertices with deg >= 2**(s - 1) - 1 
    Note : this bound should always be better (or equal) than only considering the highest degree """
    s = 1  # the bound on the size of VCdim(g)
    f_s = 0  # the min value of the ... (s - 1)-th highest degree
    
    degrees_sequence = [d for _, d in g.degree()]
    degrees_sequence.sort(reverse=True)

    if len(g.degree()) <= 2:  # just for the case of 2, which causes a bug
        return 1

    # TODO : proove this loop always terminates AND never fails (if g is not empty)
    while f_s <= degrees_sequence[s - 1]:
        # invariant : here, g may have a shattered_set of size s
        f_s = 2 * (f_s + 1) - 1
        s += 1

    # property here : impossible for g to have a shattered set of size s   
    return s - 1


# ============================== #
# TargetGraph --- test reductions in pre-processing and upper-bounding

class TargetGraph():
    def __init__(self, g : nx.Graph, ub : int):
        self.g = g
        self.ub_target = ub
        self.deg_ub = 2**(ub - 1) - 1
        self.h = {v for v in g if g.degree[v] >= self.deg_ub}  # set of nodes indicating the target inside g

        print(f"At initialisation time : {len(self.g.degree())} nodes, {len(self.h)} nodes in target")


    # BASIC STUFF

    def copy(self):
        """ not-smart copying """
        gp = TargetGraph(self.g.copy(), self.ub_target)
        return gp


    def remove_node(self, x) -> int:
        """ removes x from the graph : (from g) + (delete it from h if it was in h)
        returns 1 if x was in h """
        self.g.remove_node(x)
        if x in self.h:
            self.h.remove(x)
            return 1
        return 0


    def trace(self, x, closed=True):
        """ returns the trace of x on h, as a set of vertices (smart implementation later)
        closed indicates the convention for the neighbourhoods in the trace """
        tr_x = {v for v in self.g.neighbors(x) if v in self.h}
        return tr_x

    
    def h_induced_graph(self) -> nx.Graph:
        """ returns the graph induced by g on h """
        return nx.Graph(nx.induced_subgraph(self.g, self.h))


    # REDUCTION STRATEGIES

    def high_deg(self) -> bool:
        """ updates h to be the set of nodes with degree >= deg
        Returns true iff h was modified """
        h_copy = self.h.copy()
        for x in h_copy:
            if self.g.degree[x] < self.deg_ub:
                self.h.remove(x)

        rmvd = len(h_copy) - len(self.h)
        print(f"[high-deg] removed from H {rmvd} vertices")
        return rmvd > 0


    def rm_trace(self) -> bool:
        """ among all vertices having the same trace on h, removes all but one
        Returns true iff g was modified """
        
        traces = []  # very bad for efficiency ...
        to_remove = []

        # maybe try this to avoid bad things to happen : first the nodes of H
        for x in self.g.nodes:
            if x in self.h:
                tr_x = self.trace(x)
                if tr_x in traces:
                    to_remove.append(x)
                else:
                    traces.append(tr_x)
        

        for x in self.g.nodes:
            if x not in self.h:
                tr_x = self.trace(x)
                if tr_x in traces:
                    to_remove.append(x)
                else:
                    traces.append(tr_x)

        # print("Removing redundant vertices ... ", end="", flush=True)
        h_rmd = 0
        for x in to_remove:
            h_rmd += self.remove_node(x)
        # print("done")

        print(f"[rm_trace] removed {len(to_remove)} vertices (among which {h_rmd} from h)")
        return (len(to_remove) > 0)


    # CHECKERS

    def check_h_vertices(self) -> bool:
        """ one (basic) checker to see if we can still reach the ub """
        return len(self.h) >= self.ub_target


    def check_g_vertices(self) -> bool:
        """ another checker """
        return len(self.g) >= 2**(self.ub_target)




def graph_reduction(g : nx.Graph, ub : int) -> TargetGraph | None:
    """ reduces the graph while possible
 
    **CAUTION** : modifies the graph (TODO : check where to copy)

    Strategies implemented in the TargetGraph class :
    * high_deg : picks nodes with degree > 2**(ub - 1)
    * rm_trace : remove redundant nodes % trace on H
    
    * components : SPLITS (...) into the connected / biconnected components on H
    * modular : smth with mod decomp
    
    Returns the normal form 

    ~~or None if some error occurs / ub is not reachable~~
    (--> condition to return None : < ub vertices in H / < 2**ub vertices / ub-th vertex has degree < 2**(ub - 1) - 1 ...)
    """
    strategies = [
        TargetGraph.high_deg,
        TargetGraph.rm_trace
    ]

    checkers = [
        TargetGraph.check_h_vertices,
        TargetGraph.check_g_vertices
    ]

    tg = TargetGraph(g, ub)
    modified = True
    
    while modified:
        # we first apply the reduction strategies
        modified = False
        for strat in strategies:
            modified = strat(tg) or modified

        # we then check if it's still a valid candidate
        for chk in checkers:
            if not chk(tg):
                print(f" The checker {chk.__name__} failed; returning None")
                return None

    return tg


def reduction_ub(g : nx.Graph):
    """ computes an upper bound based on trying to reduce g
    NB : maybe mention the size of the research space at the end """
    
    start_ub = bound_on_highest_degrees(g) + 1

    improved_ub = True

    while improved_ub:
        start_ub -= 1
        improved_ub = (graph_reduction(g.copy(), start_ub) is None)  # give only a copy

    print(f"Found as ub {start_ub}")
    return start_ub


def connectivity_stats(hi : nx.Graph):
    """ Stats that would be of interest on the graph induced by h on g    
    Show connectivity, biconnectivity, ... diameter, ... degree profile ? """

    nbcc = nx.number_connected_components(hi)
    cc_sizes = [len(f) for f in nx.connected_components(hi)]
    print(f"hi has {nbcc} connected components with sizes {cc_sizes}")

    bc = nx.biconnected_components(hi)
    bc_sizes = [len(f) for f in bc]
    print(f"hi has {len(bc_sizes)} bi-connected components with sizes {bc_sizes}")
    

def main():

    graph_set = unit_data

    # <<< unit_data >>>
    # VCdims    3, 5, 3
    # bhd       6, 6, 4


    print(f"graphs are {graph_set}")
    for g_file in graph_set:
        g = build_graph_from_file(g_file)
        
        bhd = bound_on_highest_degrees(g)
        print(f"as a first bound : {bhd}")

        # _ = graph_reduction(g, bhd)
        redub = reduction_ub(g)
        print(f"FOUND {redub = } (vs {bhd = } ... ?)")

# premiers résultats : semble bien réduire ()


if __name__ == '__main__':
    main()


