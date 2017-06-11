import random
import sys
import psycopg2;


conn = psycopg2.connect("dbname=postgis_CSC_543_database user=#### password=#### host=127.0.0.1 port=5432")

cur = conn.cursor()
cur.execute("select nid,lat,long,geom from wanodes order by nid;")
rows = cur.fetchall()
j = 0
c0 =0
c1 =0
c2 = 0
c3 = 0
for i in rows:
    nid = i[0]
    lat = i[1]
    longi = i[2]
    addLat = 0.0000
    randomNumber = random.randint(0, 3)
    #print randomNumber
    #print lat,longi
    if randomNumber == 0 :
        c0 += 1
        addLat = 0.0000
    elif randomNumber == 1 :
        c1 += 1
        addLat = 0.0001
    elif randomNumber == 2 :
        c2 += 1
        addLat = 0.0002
    elif randomNumber == 3 :
        c3 += 1
        addLat = 0.0003
    #if (rows.index(i) + 6)% 8 == 0:
    #if (j + 6)% 8 == 0:
        #print 'lat : long ', lat, longi
    lat = lat + addLat
        #print 'this is 8th element at index : -------------------', rows.index(i)       
        #print 'modified lat long : ', lat, longi
    #else:
        #print rows.index(i)    
    pt = 'point(%s %s)' % (lat,longi)
    cur.execute("insert into gps3 (lat,long,geom,nid) values (%s,%s,st_geomfromtext(%s,4269),%s)",
                (lat,longi,pt,nid))
    conn.commit()
    j += 1
    #print pt, 
    #print '\n1 row with nid ---- %s ----- is inserted. counter : %s' % (nid,j)
print '\n-----------------------------------------------'
print 'counters c0 = %s, c1 = %s, c2 = %s, c3 = %s' % (c0,c1,c2,c3)



'''

---------For table gps3-------------------------------
counters c0 = 9988, c1 = 10113, c2 = 10153, c3 = 10098

#saving edges geometry
cur.execute("select eid, startnodlat,  startnodelong, intermediatenodes, endnodelat, endnodelong from waedgesgeom \
where intermediatenodes = '' and eid > 19041 and not (startnodlat = endnodelat and startnodelong = endnodelong);")
EidCol = cur.fetchall()


for i in EidCol:
    #print i
    eid = i[0]
    strpt = str(i[1]) + ' ' + str(i[2]) 
    #interpts = str(i[3]).replace('(','').replace(')',',')
    endpt = str(i[4]) + ' ' + str(i[5])
    # for intermediate points : linemerge = 'multilinestring((%s,%s%s))' % (strpt,interpts,endpt)
    linemerge = 'multilinestring((%s,%s))' % (strpt,endpt)
    #print linemerge
    print 'eid-----------------' , eid
    cur.execute("update waedgesgeom set geom = st_linemerge(st_geomfromtext(%s)) \
                where eid = %s",
                (linemerge,eid))    
    conn.commit()
    print 'edge with id %s is updated.' % (eid)
    #print '\n', interpts[:-1]


#FETCHING TRAJECTORY POINTS
cur.execute("Select lat,long from apoints500;")
trajectoryPointsCol = cur.fetchall()
minLat = -1.31484
maxLat = -1.31484
minLong = 39.86007
maxLong = 39.86007
for i in trajectoryPointsCol:
    if float(i[0]) > maxLat:
        maxLat = float(i[0])
    if float(i[0]) <= minLat:
        minLat = float(i[0])
    if float(i[1]) > maxLong:
        maxLong = float(i[1])
    if float(i[1]) <= minLong:
        minLong = float(i[1])

print 'minLat minLong : ', minLat, minLong
print 'maxLat maxLong : ', maxLat, maxLong

'''
