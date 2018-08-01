# Our Work "INT-path: Towards Optimal Path Planning for In-band Network-Wide Telemetry"


Today's data center networks have become mega-scale with increasing deployment of diverse cloud services. With the continuous expansion of network size, fine-grained network monitoring becomes the prerequisite for better network reliability and closed-loop traffic control. In traditional network monitoring, management protocols, such as SNMP, are widely adopted to constantly poll the router/switch CPU for collecting device-internal states every few seconds or minutes. However, due to the frequent interaction between the control plane and the data plane as well as the limited CPU capability, such monitoring mechanism is coarse-grained and involves a large query latency, which cannot scale well in today's high-density data center networks with drastic traffic dynamics.
 
To ameliorate the scalability issue, In-band Network Telemetry (INT) is proposed by the P4 Language Consortium (P4.org) to achieve fine-grained real-time data plane monitoring. INT allows packets to query device-internal states such as queue depth, queuing latency when they pass through the data plane pipeline, without requiring additional intervention by the control plane CPU. Typically, INT relies on a \emph{probe packet} with a variable-length label stack reserved in the packet header. The probe packets are periodically generated from an INT agent and injected into the network, where the probe packets will be queued and forwarded with the ordinary traffic. In each router/switch along the forwarding path, the probe packet will extract device-internal states and push them into the INT label stack. At the last hop, the probe packet containing the end-to-end monitoring data will be sent to the remote controller for further analysis.

INT is essentially an underlying primitive that need the support of special hardware for internal state exposure. With such data extraction interface, network operators can easily obtain the real-time traffic status of a single device or a device chain along the probing path. However, to improve network management, INT further requires a high-level mechanism built upon it to efficiently extract the network-wide traffic status. More specifically, as Software-Defined Networking (SDN) is widely deployed, the controller always expects a global view (i.e., network-wide visibility) to make the optimal traffic control decisions. Besides, network management automation via machine learning also requires timely feedback from the environment as the fed-in training data. 

In this work, we raise the concept of "In-band Network-Wide Telemetry" and propose "INT-path", a telemetry framework to achieve network-wide traffic monitoring. We tackle the problem using the divide-and-conquer design philosophy by decoupling the solution into a routing mechanism and a routing path generation policy. Specifically, we embed source routing into INT probes to allow specifying the route the probe packet takes through the network. Based on the routing mechanism, we design two INT path planning policies to generate multiple non-overlapped INT paths that cover the entire network. The first is based on depth-first search (DFS) which is straightforward but time-efficient. The second is an Euler trail-based algorithm that optimally generates non-overlapped INT paths with a minimum path number.
 
Based on INT, our approach can "encode" the network-wide traffic status into a series of "bitmap images", which further allows using advanced techniques, such as pattern recognition, to automate network monitoring and troubleshooting. Such transformation from traffic status to bitmap images will have profound significance because when the network becomes mega-scale, automated approaches are more efficient than traffic analysis purely by human efforts.


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

# DFS-based path planning algorithm

## DFLSPathPlan.py

INT path planning algorithm based on DFS.

## randomTopo.py

*createRandomTopo(sNum)* can create topologies randomly.

*createRandomTopoWithFixedOdds(oddNum, maxSNum, step)* can create topologies randomly with fixed numbers of odd vertices.

# Euler trail-based path planning algorithm

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

# How to run

If you installed the dependencies and configured the database successfully, then you can run the system with commands below

```
cd controller/
python app.py
```

You can change `graph`,`hostList` and `paths` in `app.py` to test your own network and you own INT path.
