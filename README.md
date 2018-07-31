# Our Work
Wating for Platinum

# System

The system include three modules:p4app, packet and controller.

## p4app

Include p4 source code, implemented source-based INT functrion.

header.p4, parser.p4, app.p4: p4 source code

### header.p4

Including Headers and Metadatas

### parser.p4

Including parser, deparser and checksum calculator.

### app.p4

The main part of the p4 program. Including SR/INT/ARPProxy/UDP/ECMP tables.

### app.json

The json file that compiled from app.p4 by p4c compiler.

## packet:

Send & receive INT packet module which run in the hosts and the database config.

### int_data.sql

The SQL Table which is used to initalize the database.

### receiveint.c

Used to receive int packet, and parse them, then put them into database.

### sendint.py

Use the given traverse path generate the INT packet and encode SR info.

## controller

Generate Mininet network, send SR & INT command to hosts and get result from database.

### app.py

The main controller. Use topoGraph and hostList generate netwrok, then use path to traverse the netwrok and collect INT info.

### dbParser.py

The module which is used in app.py to get INT info from database.

### device.py

The module which is used in app.py to generate the virtual devices(Hosts/Switches).

### p4_mininet.py

The module which is used in mininiet to generate P4 devices.

### switchRuntime.py

The module which is used in app.py to down tables using thrift RPC.

### topoMaker.py

The module which is used in app.py to generate network topo.

# How to run

If you installed the dependencies and configured the database successfully, then you can run the system with commands below

```
cd controller/
python app.py
```

You can change `graph`,`hostList` and `paths` in `app.py` to test your own network and you own INT path.

# algorithm

## DFLSPathPlan.py

INT path planning algorithm based on DFS.

## randomTopo.py

*createRandomTopo(sNum)* can create topologies randomly.

*createRandomTopoWithFixedOdds(oddNum, maxSNum, step)* can create topologies randomly with fixed numbers of odd vertices.

# int_path

## algorithm

### optimal_find_path_balance.py

Heuristic algorithm for balance task.

### optimal_find_path_unbalance.py

Heuristic algorithm for unbalance task.

## figure_generation

### random graph generator new.py

Heuristic algorithm for generating graph.

### randomTopo.py

Heuristic algorithm for generating graph.

### specialTopo.py

Heuristic algorithm for generating special graph, such as FatTree and SpineLeaf topo.
