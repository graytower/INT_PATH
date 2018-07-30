import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random

NUM_NODES = 20
NUM_ODD_DEGREE = 10

while(True):
    WS = nx.random_graphs.connected_watts_strogatz_graph(NUM_NODES,2,NUM_ODD_DEGREE/NUM_NODES)
    # spring layout

    count = 0
    for node in range(NUM_NODES):
        if WS.degree(node)%2!=0:
            count+=1
    # print(count)

    if count==NUM_ODD_DEGREE:

        network_matrix = np.zeros([NUM_NODES,NUM_NODES])

        for edge in WS.edges():
            # print(edge)
            network_matrix[edge[0]][edge[1]] = 1
            network_matrix[edge[1]][edge[0]] = 1

        # print(network_matrix)
        # nx.draw(WS)
        # plt.show()

        break


'''
	        op.append(network_matrix)

	        break

print(op)

# G = nx.random_graphs.connected_watts_strogatz_graph(100,4,10)
G = nx.random_graphs.barabasi_albert_graph(20, 3)

for i in range(20):
    print(G.degree(i))
print(G.edges())
for i in G.edges():
    network_matrix[i[0]][i[1]] = 1
print(network_matrix)
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels = False, node_size = 30)
plt.show()
'''
