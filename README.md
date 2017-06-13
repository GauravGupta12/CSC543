The CSC543 repository contains files for project "Map-Matching Algorithm for Tracking Vehicle Trajectory".

The following files are included in the project:

1."Road Network" folder - It Contains 4 files.
    1. WA_Nodes.txt - It contains the coordinates (lat-long format) of the points (GPS positions) that lie on the road network of the New                         York city. Each node has a unique id.
    2. WA_Edges.txt - It contains the edges which form the road network. Each edge is represented by a unique id, starting node, ending                           node and cost. The cost represents time.
    3. WA_EdgeGeometry.txt - It contains the geometry of edges. The starting node, intermediate nodes (if any), ending node and length of                                the edge.
    4. WA_Vertices.txt - It contains the vertices in lat-long format.
 
2. Create_GPS_TestData.py - This file contains Python script for creating test data (GPS point) for Map-Matching algo. Each GPS point may                             or may not match the actual GPS position on the saved road network depending on random generator function used                             in the script.

3. Map-Matching_Algo.py - This file conatins the code for Map-Matching algorithm.

4. Uploading_Road_Network.py - This file contains the scripts for loading road network for New York city into PostgreSQL database. The data                                is inserted into three different tables, one each for nodes, edges and Edgegeom.


