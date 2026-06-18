
from math import log2
import networkx as nx

# Some quick things to compute other bounds


# 1. on the number of edges :
# if S is shattered, s \in S has degree >= 2^{|S| - 1} - 1.
# We may have counted some edges twice between elements of S : 
# |S| * (2^{|S| - 1} - 1) - (|S| choose 2) <= |E|
# 
# Note : this bound is cleaner and clearer with open neighbourhoods:
# |S| * 2^{S - 1} <= |E|

def fact(n):
    if n <= 0:
        return 1
    return n * fact(n - 1)


def binom(n, k):
    return (fact(n) // (fact(k) * fact(n - k)))


def bound_on_edges(n_edges, closed=False):
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

def bound_on_highest_degrees(g):
    """ if g has a shattered set os size s, then there are s vertices with deg >= 2**(s - 1) - 1 
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


def main():
    n_edges_list = [
        68123,
        299855,
        40541,
        73762,
        31180,
        151434,
        75004,
        11095298,
        26013,
        147892,
        1090108,
        6649470,
        118489,
        1049866,
        405740,
        88234,
        1342296,
        2315222,
        1343951,
        1631574,
        2902525,
        54841
    ]

    print("[# edges] \t [bound_open] \t [bound_closed]")

    for n_edges in n_edges_list:
        b_o = bound_on_edges(n_edges)
        b_c = bound_on_edges(n_edges, True)

        print(f"{n_edges} \t {b_o} \t {b_c}")


if __name__ == '__main__':
    main()


