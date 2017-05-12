import psycopg2

conn = psycopg2.connect("dbname=xxxx user=xxxx password=xxxx host=127.0.0.1 port=5432")
cur = conn.cursor()


#SAVING NODES DATA
file = open('C:\users\\Desktop\WA_Nodes.txt')
lines = (file.read().splitlines())
counter = 0
print len(lines)
for i in lines:    
    #print i.split(' ')[0]
    nid = int(i.split(' ')[0])
    lat = i.split(' ')[1]
    longi = i.split(' ')[2]
    pt = 'Point(%s %s)' % (lat, longi)
    cur.execute("insert into wanodes (nid,lat,long,geom) values (%s,%s,%s,st_geomfromtext(%s,4269));",(nid,lat,longi,pt))
    conn.commit()
    counter += 1
    print 'row inserted , counter :', counter



# SAVING EDGES DATA
file = open('C:\users\\Desktop\WA_Edges.txt')

lines = (file.read().splitlines())
counter = 0
print len(lines)
for i in lines:    
    #print type(i.split(' ')[0])
    eid = (i.split(' ')[0])
    strtnode = (i.split(' ')[1])
    endnode = (i.split(' ')[2])
    etcost = float(i.split(' ')[3])
    #print type(strtnode), endnode
    cur.execute("select st_astext(geom) from wanodes where nid = (%s);",(i.split(' ')[1],))
    startnoderow = cur.fetchall()
    strtnodegeom = str(startnoderow[0])[2:][:-3]
    #print 'strtnodegeom :', strtnodegeom
    cur.execute("select st_astext(geom) from wanodes where nid = (%s);",(i.split(' ')[2],))
    endnoderow = cur.fetchall()
    endnodegeom = str(endnoderow[0])[2:][:-3]
    cur.execute("insert into waedges (eid,startnode,endnode,startnodegeom,endnodegeom,etcost) values (%s,%s,%s,st_geomfromtext(%s,4269),st_geomfromtext(%s,4269),%s);",
                (eid,strtnode,endnode,strtnodegeom,endnodegeom,etcost))
    conn.commit()
    counter += 1
    print 'row inserted , counter :', counter



# SAVING EDGES GEOMETRY DATA
file = open('C:\users\\Desktop\WA_EdgeGeometry.txt')

lines = (file.read().splitlines())
counter = 0
print len(lines)
missedrows = 0
for i in lines:
    if i != '':
        arr = i.split('^')
        if len(arr) >=8:                    
            eid = arr[0]
            ename = arr[1]
            etype = arr[2]
            elen = arr[3]
            eslat = arr[4]
            eslong = arr[5]
            startgeom = 'point(%s %s)' % (eslat,eslong)
            inodes = ''
            if len(arr) > 8:
                j = 6            
                while j < len(arr)-2:
                    if j%2 == 0:
                        inodes = inodes + '(' + arr[j]
                    else:
                        inodes = inodes + ' ' + arr[j] + ')'            
                    j += 1
            eelat = arr[len(arr)-2]
            eelong = arr[len(arr)-1]
            endgeom = 'point(%s %s)' % (eelat,eelong)
            cur.execute("insert into waedgesgeom (eid,Ename,Etype,Elength,startnodlat,startnodelong,startnodegeom,intermediatenodes,endnodelat,endnodelong,endnodegeom) \
                        values (%s,%s,%s,%s,%s,%s,st_geomfromtext(%s,4269),%s,%s,%s,st_geomfromtext(%s,4269))",
                        (eid,ename,etype,elen,eslat,eslong,startgeom,inodes,eelat,eelong,endgeom))
            conn.commit()
            counter += 1
            print 'row inserted , row counter :', counter
        elif len(arr) < 8:
            missedrows += 1
            print '------------------------------------edge missed with id : -------- ',arr[0]

print 'number of missed rows : ', missedrows


        
'''

create table WAEdgesGeom(
 eid int primary key,
 Ename varchar,
 Etype varchar,
 Elength float,
 startnodlat float,
 startnodelong float,
 startnodegeom geometry,
 intermediatenodes varchar,
 endnodelat float,
 endnodelong float,
 endnodegeom geometry,
 etcost float,
 constraint fk_eid FOREIGN key (eid) references waedges (eid)
)
/*
create table WAEdges(
 eid int primary key,
 startnode int,
 endnode int,
 startnodegeom geometry,
 endnodegeom geometry,
 etcost float,
 constraint fk_starrtnode FOREIGN key (startnode) references wanodes (nid),
 constraint fk_endnode FOREIGN key (endnode) references wanodes (nid)
)
-- select addgeometrycolumn('WAEdges','geom',4269,'line',2)

create table WANodes(
 nid int primary key,
 lat float,
 long float   
)
select addgeometrycolumn('wanodes','geom',4269,'point',2)


*/

'''
