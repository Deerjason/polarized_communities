import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")

import argparse
import numpy as np

from signed_graph.signed_graph import SignedGraph

from algorithms.eigensign import eigensign
from algorithms.random_eigensign import random_eigensign

from algorithms.bansal import bansal
from algorithms.local_search import local_search

from algorithms.greedy_degree_removal import greedy_degree_removal

from utilities.print_console import print_input

if __name__ == '__main__':
    # create a parser
    parser = argparse.ArgumentParser(description='Hidden Polarized Communities')

    # create and read the arguments
    parser.add_argument('d', help='dataset', type=str)
    parser.add_argument('a', help='algorithm', type=str)
    parser.add_argument('-mi', help='maximum iterations', type=int, default=np.inf)
    parser.add_argument('-ct', help='convergence threshold', type=float, default=0.2)
    parser.add_argument('-b', help='multiplicative factor for random_eigensign', type=str, default='l1')

    args = parser.parse_args()

    # read the input graph
    signed_graph = SignedGraph(args.d)

    print_input(args.d, args.a)
    # execute the algorithm
    if args.a == 'eigensign':
        solution, x = eigensign(signed_graph)

    elif args.a == 'random_eigensign':
        solution, x, maximum_eigenvector, execution_time_seconds, beta = random_eigensign(signed_graph, args.b)

    elif args.a == 'bansal':
        solution, x = bansal(signed_graph)

    elif args.a == 'random_local':
        solution, x = local_search(signed_graph, args.mi, args.ct)

    elif args.a == 'greedy_signed_degree':
        solution, x = greedy_degree_removal(signed_graph)

    if args.a == 'eigensign' or args.a == 'bansal' or args.a == 'greedy_signed_degree':
        f = open(args.d + '_' + args.a + '_subgraphs', 'w')
        adj = signed_graph.get_adjacency_matrix()
        S_1 = []
        S_2 = []
        S = []
        for u in solution:
            if x[u] == -1:
                S_2.append(u)
                S.append(u)
            elif x[u] == 1:
                S_1.append(u)
                S.append(u)
        if len(S_2) > len(S_1):
            S_1, S_2 = S_2, S_1
        if len(S_2) == 0:
            for node in S_1:
                f.write(str(node) + ' ')
            f.write('-1 -1\n')
        else:
            for node in S_1:
                f.write(str(node) + ' ')
            f.write('-1 ')
            for node in S_2:
                f.write(str(node) + ' ')
            f.write('-1\n')
        subG = S
        num_nodes = 0
        while signed_graph.number_of_nodes != num_nodes:
            signed_graph_ = SignedGraph(None, signed_graph.number_of_nodes, adj, set(subG))
            adj = signed_graph_.get_adjacency_matrix()

            if args.a == 'eigensign':
                solution, x = eigensign(signed_graph_)
            elif args.a == 'bansal':
                solution, x = bansal(signed_graph_)
            elif args.a == 'greedy_signed_degree':
                solution, x = greedy_degree_removal(signed_graph_)
            S_1 = []
            S_2 = []
            S = []
            for u in solution:
                if x[u] == -1:
                    S_2.append(u)
                    S.append(u)
                elif x[u] == 1:
                    S_1.append(u)
                    S.append(u)
            num_nodes = len(S)
            if num_nodes < 10:
                break
            if len(S_2) > len(S_1):
                S_1, S_2 = S_2, S_1
            if len(S_2) == 0:
                for node in S_1:
                    f.write(str(node) + ' ')
                f.write('-1 -1\n')
            else:
                for node in S_1:
                    f.write(str(node) + ' ')
                f.write('-1 ')
                for node in S_2:
                    f.write(str(node) + ' ')
                f.write('-1\n')
            subG = S
        f.close()
