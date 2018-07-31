#!/usr/bin/python
import random
import sys
import copy
import randomTopo

def DFLSPathPlan(topoMatrix, sNum):
	sys.setrecursionlimit(1000000)
	linkState = copy.deepcopy(topoMatrix)
	pathCount = [0]
	#DFLS
	def DFLS(v, isNewPath):
		if isNewPath == 1:
			# print " "
			# print v, " "
			pathCount[0] += 1
			isNewPath = 0
		# else:
		# 	print v, " "
		for j in range(sNum):
			if linkState[v][j] == 1:
				linkState[v][j] = 0
				linkState[j][v] = 0
				isNewPath = DFLS(j, isNewPath)
		return 1
	DFLS(0,1)
	return pathCount[0]

if __name__ == '__main__':
	sNum = 100
	topoMatrix = randomTopo.createRandomTopo(sNum)
	pathNum = DFLSPathPlan(topoMatrix, sNum)
	print pathNum
	