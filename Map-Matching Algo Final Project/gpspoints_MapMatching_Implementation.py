import sys
import psycopg2;
import math

conn = psycopg2.connect("dbname=postgis_CSC_543_database user=#### password=#### host=127.0.0.1 port=5432")

def CreateCandidateSet(p_gpsPointsCol):
    #conn = psycopg2.connect("dbname=postgis_CSC_543_database user=postgres password=postgres host=127.0.0.1 port=5432")
    cur = conn.cursor()
    CandidateEdgesColl = []
    for i in p_gpsPointsCol:
        #print i[0], i[1],i[2],i[3]
        pt = 'point(%s %s)' % (i[1],i[2])
        #print 'trajectory point : ',pt
        cur.execute("select nid,lat,long d_meters from \
        (SELECT nid, geom ,lat,long, st_distance(st_geomfromtext(%s,4269),geom)*100000 d_meters \
         FROM wanodes ORDER BY geom <-> st_geomfromtext(%s,4269) LIMIT 50) as f11 \
         where d_meters <= 18;",(pt,pt))
        rows_18m_pts = cur.fetchall()
        EachclosePt = []
        if len(rows_18m_pts) > 0:
            #print "\ncandiates of point within 18 meters of distance ------- : ---------------------\n"
            #print 'gps point : ',i[1],i[2]
            CandidateRowsforeachClosePt = []
            for j in rows_18m_pts:
                cpt = 'point(%s %s)' % (j[1],j[2])
                #print 'candidate point ', cpt
                cur.execute("select eg.eid,startnodlat,startnodelong,endnodelat,endnodelong, etcost \
                            from waedgesgeom eg join waedges e on eg.eid=e.eid where e.startnodegeom = eg.startnodegeom \
                            and e.endnodegeom = eg.endnodegeom and st_covers(geom,st_geomfromtext(%s,4269)) order by eid;",(cpt,))
                CandidateRowsforeachClosePt = cur.fetchall()
                EachclosePt.append(CandidateRowsforeachClosePt)
                #print 'Candidate Rows are -------------- :' 
                for k in CandidateRowsforeachClosePt:
                    #print k
                    m = 1
                #print j
        CandidateEdgesColl.append(EachclosePt)
        #print '-------------------------------------------------------'
    #conn.close()
    return CandidateEdgesColl

def CalculateAngleBetweenEdge_Trjpt(edge,currentPoint,previousPoint):
    #conn = psycopg2.connect("dbname=postgis_CSC_543_database user=postgres password=postgres host=127.0.0.1 port=5432")
    cur = conn.cursor()
    #print currentPoint
    currpt = 'point(%s %s)' % (currentPoint[1],currentPoint[2])
    prevpt = 'point(%s %s)' % (previousPoint[1],previousPoint[2])
    cur.execute("SELECT ST_Azimuth(st_geomfromtext(%s,4269),st_geomfromtext(%s,4269))/(2*pi())*360 angle1;",
                (currpt,prevpt))
    angle_points = cur.fetchall()
    a1 = 0
    if str(angle_points)[2:][:-3] != 'None':
        a1 = float(str(angle_points)[2:][:-3])
        #print 'a1 is ', a1
    e_st_pt = 'point(%s %s)' % (edge[1],edge[2])
    e_end_pt = 'point(%s %s)' % (edge[3],edge[4]) 
    cur.execute("SELECT ST_Azimuth(st_geomfromtext(%s,4269),st_geomfromtext(%s,4269))/(2*pi())*360 angle1;",
                (e_st_pt,e_end_pt))
    angle_edge = cur.fetchall()
    a2 = 0
    if str(angle_edge)[2:][:-3] != 'None':
        a2 = float(str(angle_edge)[2:][:-3])
        #print 'a2 is ', a2
    #print float(str(angle_edge)[2:][:-3])
    diffangle = a1 - a2;
    #print ' %s,  %s, %s', (angle_points,angle_edge,diffangle)
    #print 'angle diff -----------------------------------', (diffangle)
    #conn.close()
    return diffangle;    

def RefineCandidateSet(p_CandidateEdgesCol,p_gpsPointsCol):
    #conn = psycopg2.connect("dbname=postgis_CSC_543_database user=postgres password=postgres host=127.0.0.1 port=5432")
    cur = conn.cursor()
    RefinedEdegesSet = []
    #refined_closept_col = []
    #refined_edges_col = []
    m = 0
    for closeptCol in p_CandidateEdgesCol:
        #if m >0:
        n = 0
        refined_closept_col = []
        for closeptEdgecol in closeptCol:
            refined_edges_col = []
            q = 0
            #print '\n'
            for edge in closeptEdgecol:
                #print 'angles at collection index :-------------',m,n,q,edge
                if m >0:
                    angle = CalculateAngleBetweenEdge_Trjpt(edge,p_gpsPointsCol[m],p_gpsPointsCol[m-1])
                    #print angle
                    if angle >= 0 and angle <= 90 :
                        refined_edges_col.append(edge)
                elif m == 0:
                    #print 'm = 0'
                    angle = CalculateAngleBetweenEdge_Trjpt(edge,p_gpsPointsCol[m],p_gpsPointsCol[m+1])
                    #print angle
                    if angle >= 0 and angle <= 90 :
                        refined_edges_col.append(edge)
                    #refined_edges_col.append(edge)
                q += 1
            refined_closept_col.append(refined_edges_col)
            #print 'last edge is this last collection was : and its angle ', edge
            #print 'angle refined edges at -------------------------',m,n, q
            #print '\n'
            for p in refined_edges_col:
                a = 0
                #print p;
            n = n + 1
        RefinedEdegesSet.append(refined_closept_col)
        m = m + 1
    #conn.close()
    return RefinedEdegesSet;

def ComputeQualityScore(p_inputEdgesCol,currentpt,previousPoint):
    qualityScoredEdgesSet = p_inputEdgesCol
    qualityScoredEdgesSet_final = p_inputEdgesCol
    dict_scores = {}
    maxscore = -999999999999999999999999.0
    Mu_alpha = 10
    c_alpha = 4
    Mu_d = 0.17
    c_d = 1.4    
    currpt = 'point(%s %s)' % (currentpt[1],currentpt[2])
    prevpt = 'point(%s %s)' % (previousPoint[1],previousPoint[2])
    for edge in p_inputEdgesCol:
        eid = edge[0]
        #print 'input edge -------------',edge
        cur.execute("select st_distance(st_geomfromtext(%s,4269),st_makeline(geom))*100000 e_distance from \
                    (select geom from waedgesgeom where eid = %s) as f22;"
                    ,(currpt,eid))
        e_distance = cur.fetchall()
        #print 'distance --',float(str(e_distance[0])[1:][:-2])
        angle_btw_pt_n_edge = CalculateAngleBetweenEdge_Trjpt(edge,currentpt,previousPoint)
        score = (Mu_alpha * pow(math.cos(math.radians(angle_btw_pt_n_edge)),c_alpha)) - (Mu_d * pow(float(str(e_distance[0])[1:][:-2]),c_d))
        dict_scores[eid] = score
        if score >= maxscore:
            maxscore = score
        #print 'score ------------------',score
        #print 'maxscore ---------------',maxscore
    for key, value in dict_scores.iteritems():
        #print 'dictionary key -------------------------',key, dict_scores[key], value
        if value < maxscore * 0.8:            
            eid_remove = [t[0] for t in p_inputEdgesCol if t[0] == key]
            #print 'filtering --', eid_remove
            #qualityScoredEdgesSet.append([t for t in p_inputEdgesCol if t[0] == key])
            qualityScoredEdgesSet_final = filter(lambda x: str(x[0]) != str(eid_remove)[1:][:-1], qualityScoredEdgesSet_final)
            #for i in qualityScoredEdgesSet_final:
            #    print i,i[0]
            #qualityScoredEdgesSet.remove(edge_remove)
            #del dict_scores[key]
    #print 'dictionary aftr deleteig keys--------'
    #print 'final score-refined edges are --'
    for i in qualityScoredEdgesSet_final:
         a = 0#print i
    return qualityScoredEdgesSet_final;


def CreatePtCandidateEdgeInsSet(RefinedEdegesSet,gpsPointsCol):
    ptCandidateEdgeInsSet = []
    m = 0
    for trjpt in RefinedEdegesSet:
        #print '\n--- Trajectory point %s  ------------------------------------------------------' % (m + 1)
        n = 0
        EachPt_CEdge_Set = []
        for closept in trjpt:
            #print '\n----- close points  %s  -----' % (n)           
            for edge in closept:
                #print edge
                pt = 'point(%s %s)' % (gpsPointsCol[m][1],gpsPointsCol[m][2])
                eid = edge[0]
                #print 'eid = ',eid
                #lineStartpt = 'point(%s %s)' % (edge[1], edge[2])
                #lineEndpt = 'point(%s %s)' % (edge[3], edge[4])
                cur.execute("select st_intersects(st_geomfromtext(%s,4269),geom), \
                            st_astext(st_intersection(st_geomfromtext(%s,4269),geom)), etcost from waedgesgeom eg join waedges e on eg.eid=e.eid \
                            where eg.eid = %s and e.startnodegeom = eg.startnodegeom and e.endnodegeom = eg.endnodegeom ;",(pt,pt,eid))
                result = cur.fetchall()
                #print 'Point %s intersects edge %s : %s' % (pt,edge[0],result[0])
                #print result[0][0], result[0][1],result[0][2],
                if str(result[0][0]) == 'True':
                    #print 'its true'
                    if result[0] not in EachPt_CEdge_Set:
                        EachPt_CEdge_Set.append(result[0])
                    #else:
                    #    print result[0][1], 'already presentin the set'
            n = n + 1
            #print '-----------------------------------', m,n
        m = m + 1
        ptCandidateEdgeInsSet.append(EachPt_CEdge_Set)
    ctr = 0
    a=0#print '-=-=-==-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-='
    for i in ptCandidateEdgeInsSet:
        for q in i:
            a=0#print q
        ctr += 1
        a=0#print '---------------------------------', ctr
    return ptCandidateEdgeInsSet;

#Main function 
#conn = psycopg2.connect("dbname=postgis_CSC_543_database user=postgres password=postgres host=127.0.0.1 port=5432")
cur = conn.cursor()
#FETCHING TRAJECTORY POINTS
noofpoints = 48  # gpspoints 101-148, 149-157, 158-163, 164-170, 171-174, 175-181 |---| gps2 points  
print 'number of gps points :', noofpoints
cur.execute("Select nid,lat,long,geom from gpspoints where pid > 100 order by pid limit %s;",(noofpoints,))
gpsPointsCol = cur.fetchall()
CandidateEdgesColl = CreateCandidateSet(gpsPointsCol)

m = 0
for trjpt in CandidateEdgesColl:
    a=0#print '\n--- Trajectory point %s  ------------------------------------------------------' % (m + 1)
    n = 0
    for closept in trjpt:
        a=0#print '\n----- close points  %s  -----' % (n)
        for edge in closept:
            a=0#print edge
        n = n + 1
    m = m + 1


RefinedEdegesSet = RefineCandidateSet(CandidateEdgesColl,gpsPointsCol)

print len(CandidateEdgesColl)
print len(RefinedEdegesSet)

m = 0
for trjpt in RefinedEdegesSet:
    #print '\n--- Trajectory point %s  ------------------------------------------------------' % (m + 1)
    n = 0
    for closept in trjpt:
        #print '\n----- close points  %s  -----' % (n)
        if len(closept) > 0:            
            for edge in closept:
                a = 0#print edge
        else:
            qualityScoredEdgesSet = ComputeQualityScore(CandidateEdgesColl[m][n],gpsPointsCol[m],gpsPointsCol[m-1])
            #print 'replaced edges collection at index i below :',m,n
            RefinedEdegesSet[m][n] = []
            RefinedEdegesSet[m][n] = qualityScoredEdgesSet
        n = n + 1
    m = m + 1

#print 'final list after all refinements : ==============================='
m = 0
for trjpt in RefinedEdegesSet:
    #print '\n--- Trajectory point %s  ------------------------------------------------------' % (m + 1)
    n = 0
    for closept in trjpt:
        #print '\n----- close points  %s  -----' % (n)           
        for edge in closept:
            a=0#print edge
        n = n + 1
    m = m + 1

geomstring = 'Linestring('
ptCandidateEdgeInsSet = CreatePtCandidateEdgeInsSet(RefinedEdegesSet,gpsPointsCol)
minWeight = 99999999999.999999999999
minWeightPtString = ''
for i in ptCandidateEdgeInsSet:
    minWeight = 99999999999.999999999999
    minWeightPtString = ''
    for q in i:
        if q[2] <= minWeight:
            minWeight = q[2]
            minWeightPtString = str(q[1])[6:][:-1]
        #print str(q[1])[6:][:-1], (q[2])
    print minWeight, minWeightPtString
    if minWeightPtString != '':
        #print 'minWeightPtString is not empty----------------'
        geomstring = geomstring + minWeightPtString + ','
    #print '###########################'
#print 'geomstring : \n',geomstring
    
geomstring = geomstring[:-1] + ')'
cur.execute("select st_astext(st_linemerge(st_geomfromtext(%s)))",(geomstring,))
finalgpstrajectory = cur.fetchall()
print str(finalgpstrajectory[0])[2:][:-3]

conn.close();

print "\nExecution completed."


