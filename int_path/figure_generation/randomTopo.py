#!/usr/bin/python
import random
import sys
import numpy as np
import copy

def createRandomTopo(sNum):
	sys.setrecursionlimit(1000000)
	#create adjaMatrix
	topoMatrix = [[0 for i in range(sNum)] for i in range(sNum)]
	visited = [0 for i in range(sNum)]
	#create topo randomly
	for i in range(sNum):
		for j in range(i+1, sNum):
			link = random.randint(0,1)
			topoMatrix[i][j] = link
			topoMatrix[j][i] = link
	#DFS
	def DFS(v):
		visited[v] = 1
		for j in range(sNum):
			if topoMatrix[v][j] == 1 and visited[j] == 0:
				DFS(j)
	#check the network connectivity using DFS
	disconNode = []
	for i in range(sNum):
		if visited[i] == 0:
			DFS(i)
			disconNode.append(i)
	#if the network is unconnected, connect each disconNode
	for i in range(len(disconNode)-1):
		topoMatrix[disconNode[i]][disconNode[i+1]] = 1
		topoMatrix[disconNode[i+1]][disconNode[i]] = 1

	oddCount = calOddNum(topoMatrix, sNum)

	return topoMatrix, oddCount

def createRandomTopoWithFixedOdds(oddNum, maxSNum, step=1):
	sys.setrecursionlimit(1000000)
	sNum = 2*oddNum
	topoLists = []

	while sNum <= maxSNum:
		flag = 0
		while flag != 1:
			#create adjaMatrix
			topoMatrix = g_generator_edge(10000, sNum)
			for i in topoMatrix:
				oddCount = calOddNum(i, sNum)
				if oddCount == oddNum:
					topoLists.append(i)
					print("sNum ", sNum)
					flag = 1
					break
		sNum += step

	return topoLists

def calOddNum(topoMatrix, sNum):
	count = 0
	for i in range(sNum):
		degreeSum = 0
		for j in range(sNum):
			degreeSum += topoMatrix[i][j]
		if degreeSum%2 == 1:
			count += 1
	return count

def g_generator_edge(NUM_GRAPHS,NUM_NODES,edge_incre=1):
	op=[]
	NUM_GRAPHS=min(NUM_GRAPHS,int(NUM_NODES*(NUM_NODES-1)/2-NUM_NODES))
	for i in range(NUM_GRAPHS):
		if(i==0):
			network_matrix=np.zeros([NUM_NODES, NUM_NODES])
			for j in range(NUM_NODES-1):
				network_matrix[j][j+1] = 1
				network_matrix[j+1][j]=1
			network_matrix[0][NUM_NODES-1]=1
			network_matrix[NUM_NODES-1][0]=1
			op.append(network_matrix)
		else:
			network_matrix=copy.deepcopy(op[i-1])
			select=[]
			for j in range(NUM_NODES):
				for k in range(j+1,NUM_NODES):
					if(network_matrix[j][k]==0):
						select.append([j,k])
			for l in range(edge_incre):
				temp=select.pop(random.randint(0,len(select)-1))
				network_matrix[temp[0]][temp[1]]=1
				network_matrix[temp[1]][temp[0]]=1
			op.append(network_matrix)
	return op


if __name__ == '__main__':
	sNum = 5
	topo, oddCount = createRandomTopo(sNum)
	print(topo)
	print(oddCount)
	topoList = createRandomTopoWithFixedOdds(20,200,5) #each sNum has five graphs
	print(topoList)