The CSC543 repository contains files for project "Map-Matching Algorithm for Tracking Vehicle Trajectory".

The following files are included in the project:

1."Road Network" folder - It Contains 4 files.

    1. WA_Nodes.txt - It contains the coordinates (lat-long format) of the points (GPS positions) that lie on the road network of the New                         York city. Each node has a unique id.
    
    2. WA_Edges.txt - It contains the edges which form the road network. Each edge is represented by a unique id, starting node, ending                           node and cost. The cost represents time.
                      An edge from point A to point B, is different from an edge from point B to A.
                      Both edges are saved separately with unique id.
                      
    3. WA_EdgeGeometry.txt - It contains the geometry of edges. The starting node, intermediate nodes (if any), ending node and length of                                the edge.
    
    4. WA_Vertices.txt - It contains the vertices in lat-long format.
 
2. Create_GPS_TestData.py - This file contains Python script for creating test data (GPS point) for Map-Matching algo. Each GPS point may                             or may not match the actual GPS position on the saved road network depending on random generator function used                             in the script. 
                          There are 40,352 GPS points created (equal to number of nodes in WA_Nodes.txt files).

3. Map-Matching_Algo.py - This file conatins the code for Map-Matching algorithm.

4. Uploading_Road_Network.py - This file contains the scripts for loading road network for New York city into PostgreSQL database. The data                                is inserted into three different tables, one each for nodes, edges and Edgegeom.
                               There are 40,352 nodes in the Nodes table.
                               There are 33,326 edges in the Edges table.
                               There 29,626 entries in the Edgegeom table. (more than 3000 edges have incorrect geometry, end points are                                  missing for such edges)

