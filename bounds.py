
from math import log2
import networkx as nx
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

# TODO : add bound with nodes, get things from data ...
# observation : almost always = to deg or 1 less, sometimes worse, always higher than \Delta

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


class TargetGraph(nx.Graph):
    ...


def graph_reduction(tg : TargetGraph, ub : int) -> TargetGraph | None:
    """ reduces the graph while possible
    Strategies : 
    * high_deg : picks nodes with degree > 2**(ub - 1)
    * (nope) coreness : picks node present in a ub-1 - core
    * rm_trace : remove redundant nodes % trace on H
    * components : SPLITS (...) into the connected / biconnected components ?
    * modular : smth with mod decomp
    
    Returns the normal form or None if some error occurs / ub is not reachable
    """
    raise NotImplementedError


def reduction_ub(g : nx.Graph):
    """ computes an upper bound based on trying to reduce g
    NB : maybe mention the size of the research space at the end """
    ...



def main():
    ...

if __name__ == '__main__':
    main()


