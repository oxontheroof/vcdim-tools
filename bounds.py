
from math import log2
import networkx as nx
from io_data import build_graph_from_file, graphs_2024_sorted, graphs_2023, graphs_unit
from typing import Set
# import sage.all as sa



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


def compare_sequences(seq1, seq2) -> bool:
    """ compares two sequences elements by elements, until one is exhausted 
    Returns True iff (seq1 >= seq2) """
    for x1, x2 in zip(seq1, seq2):
        if x1 < x2:
            return False
    return True


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


# def core_ordering(g : nx.Graph):
#     """ returns a list of nodes that is a k-core ordering of the graph """
#     g_cop = g.copy
#     degree_buckets = [[] for _ in range(len(g) + 1)]

#     for node in g.nodes():
#         degree_buckets[g.degree()[node]].append(node)
#     
#     return ordering


# ============================== #
# TargetGraph --- test reductions in pre-processing and upper-bounding

class TargetGraph():
    def __init__(self, g : nx.Graph, ub : int):

        assert (ub > 2)  # else the problem is quite easy

        self.g = g
        self.ub_target = ub
        self.deg_lb = 2**(ub - 1) - 1  # actually a lower bound on the degrees
        self.h = {v for v in g if g.degree[v] >= self.deg_lb}  # set of nodes indicating the target inside g

        
        self.__local_neighbourhood_ub = [-1] * (len(g) + 1)  # (not initialized) ub of the size of S shattered contained in N[i]
        # we will be interested in the comparison with the following sequence : 

        self.__least_local_neighbourhood_ub = []
        # instead of building the whole sequence, we restrict ourselves to the 
        for bnd, nb in [(ub, 1), (ub - 1, ub - 1), (ub - 2, ((ub - 2) * (ub - 1)) // 2)]:
            self.__least_local_neighbourhood_ub.extend([bnd] * nb)
            

        print(f"At initialisation time : {len(self.g.degree())} nodes, {len(self.h)} nodes in target; target ub = {self.ub_target}")


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


    def trace(self, x, closed=True) -> Set:
        """ returns the trace of x on h, as a set of vertices (smart implementation later)
        closed indicates the convention for the neighbourhoods in the trace """
        tr_x = {v for v in self.g.neighbors(x) if v in self.h}
        return tr_x

    
    def trace_neighbourhood(self, x, y, closed=True):
        """ returns the trace of x on N[y] cap H """
        tr_x = self.trace(x, closed=closed)
        tr_x_on_ny = {v for v in self.g.neighbors(y) if v in tr_x}
        return tr_x_on_ny


    def compute_local_neighbourhood_ub(self, x) -> int:
        """ Computes the local upper-bound on a shattered set included in N[x]

        Several properties can be used (we would take the min of them): 

        * large-trace : u' s.t there are at least 2^u' distinct traces on N[x]
        * [NOT USED] highest-degrees : the ub largest degrees must be at least self.deg_lb

        Returns the bound (can be lower than self.ub_target)
        """
        traces = [self.trace_neighbourhood(x, x)]  # very bad efficiency
        for z in self.g.neighbors(x):  # restriction to the vertices at distance <= 2
            tr_xz = self.trace_neighbourhood(z, x)
            if tr_xz not in traces:
                traces.append(tr_xz)
            
            for y in self.g.neighbors(z):
                tr_xy = self.trace_neighbourhood(y, x)
                if tr_xy not in traces:
                    traces.append(tr_xy)

        add_empty = 1 if (len(self.g[x]) < len(self.g.nodes()) - 1) else 0

        return int(log2(len(traces) + add_empty))


    def compute_local_neighbourhood_ub_all(self):
        """ Recomputes the entire __local_neighbourhood_ub array """
        print(f"{self.__least_local_neighbourhood_ub}")
        for x in self.g.nodes():
            self.__local_neighbourhood_ub[x] = self.compute_local_neighbourhood_ub(x)

        # assert(all(i > 0 for i in self.__least_local_neighbourhood_ub))  # the entire list should be filled


    def compute_local_point_ub(self, x) -> bool:
        """ Computes a local ub on the size of a shattered set containing x
        This shall be used only when self.local_neighbourhood_ub was called

        Several properties can be used : 

        * neighbourhood_seq : the list of decreasing local_neighbourhood_ub must be >= __least_...

        * TODO: find something with ball reduction (see timing tables of article)

        Returns True iff (local_ub for x >= ub_target)
        """
        local_neighbourhood_ub_seq_x = [self.__local_neighbourhood_ub[y] for y in self.g[x]]
        local_neighbourhood_ub_seq_x.append(self.__local_neighbourhood_ub[x])
        local_neighbourhood_ub_seq_x.sort(reverse=True)

        cmp = compare_sequences(local_neighbourhood_ub_seq_x, self.__least_local_neighbourhood_ub)
        if not cmp:
            # print(f"cmp is False, with {x}, whose neighbours have {local_neighbourhood_ub_seq_x}")
            ...
        return cmp

    
    def h_induced_graph(self) -> nx.Graph:
        """ returns the graph induced by g on h, i.e G[H] """
        return nx.Graph(nx.induced_subgraph(self.g, self.h))


    # REDUCTION STRATEGIES

    def high_deg(self) -> bool:
        """ updates h to be the set of nodes with degree >= deg
        Returns true iff h was modified """
        h_copy = self.h.copy()
        for x in h_copy:
            if self.g.degree[x] < self.deg_lb:
                self.h.remove(x)

        rmvd = len(h_copy) - len(self.h)
        print(f"[high-deg] removed {rmvd} vertices from H")
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

        print(f"[rm_trace] removed {len(to_remove)} vertices (among which {h_rmd} from H)")
        return (len(to_remove) > 0)

    
    def neighbourhood_traces(self) -> bool:
        """ Applies the reduction rule corresponding to local upper bound on a shattered set included in a neighbourhood 
        
        Returns True iff the graph (H) was modified
        """
        self.compute_local_neighbourhood_ub_all()
        # print(f"{self.__local_neighbourhood_ub[:20] = }")
        to_remove = []
        for x in self.h:
            if not self.compute_local_point_ub(x):
                to_remove.append(x)
        
        for x in to_remove:
            self.remove_node(x)

        print(f"[neighbourhood_traces] removed {len(to_remove)} vertices (from H)")
        return (len(to_remove) > 0)


    def high_core(self) -> bool:
        """ [USELESS] retains only the vertices of H in a (ub - 1)-core 
        Returns true iff h was modified """

        # as before, very unefficient implementation for this time
        core_nums = nx.core_number(self.g)

        h_c = self.h.copy()
        for x in h_c:
            if core_nums[x] < self.ub_target - 1:
                self.h.remove(x)
        
        rmvd = len(h_c) - len(self.h)
        print(f"[high_core] removed {rmvd} vertices from H")
        return (rmvd > 0)

    
    def high_local_ub(self) -> bool:
        """ TODO Retains in h only the vertices with a high enough local_bound """
        ...

    def modular_decomposition_split(self) -> bool:
        """ Something to use the MD of g : 
        
        compute it, assign in H the modules id, go down to nodes we can restrict ourselves to,
        then see if still enough nodes / enough parts
        
        maybe provide / display smth about repartition of H, how much it reduces the space """
        ...

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
    
    * neighbourhood_bound : a shattered set included in N[x] has a bound depending on traces on N[x] (ub on v would be max of this on N[x] containing v)

    SPLITS (will be handled by another function)
    * components : splits (...) into the connected / biconnected components on H --- may not be that useful
    * modular : smth with mod decomp --- about H included in small number of modules ?
    

    USELESS (unless improved)
    * coreness : vertices must be in a (ub-1)-core (and the coreness may vary when removing vertices)


    Returns the normal form 

    ~~or None if some error occurs / ub is not reachable~~
    (--> condition to return None : < ub vertices in H / < 2**ub vertices / ub-th vertex has degree < 2**(ub - 1) - 1 ...)
    """
    strategies = [
        TargetGraph.high_deg,
        TargetGraph.rm_trace,
        TargetGraph.neighbourhood_traces  # this order seems better for the reduction ...
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

    # about the efficiency of the reduction :
    print(" --- REDUCTION EFFICIENCY : --- ")
    prc = int((100 * len(tg.h) / tg.g.size()))
    print(f" |G| = {tg.g.size()}, |H| = {len(tg.h)} ({prc}%)")

    # TMP : provide some informations about G[H] :
    hind = tg.h_induced_graph()
    print(" --- About G[H] : --- ")
    connectivity_stats(hind)
    return tg


def reduction_ub(g : nx.Graph):
    """ computes an upper bound based on trying to reduce g
    NB : maybe mention the size of the research space at the end """
    
    start_ub = bound_on_highest_degrees(g) + 1

    improved_ub = True

    while improved_ub and start_ub > 2:
        start_ub -= 1
        if start_ub > 2:
            improved_ub = (graph_reduction(g.copy(), start_ub) is None)  # give only a copy

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

    graph_set = graphs_unit  # graphs_2023[:10]  # graphs_2024_sorted[:10]

    # <<< unit_data >>>
    # VCdims    3, 5, 3
    # bhd       6, 6, 4
    # redub     4, 6, 4


    # <<< small_set >>>
    # VCdims    4, 4, 5, 5, 4
    # bhd       6, 6, 8, 8, 7
    # redub     5, 5, 6, 6, 6


    print(f"graphs are {graph_set}")


    for g_file in graph_set:
        g = build_graph_from_file(g_file)
        
        bhd = bound_on_highest_degrees(g)
        print(f"as a first bound : {bhd}")

        # _ = graph_reduction(g, bhd)
        redub = reduction_ub(g)
        print(f"FOUND {redub = } (vs {bhd = } ... ?) \n\n")

# premiers résultats : réduit, mais légèrement seulement (prévisible)


if __name__ == '__main__':
    main()


