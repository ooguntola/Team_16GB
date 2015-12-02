# This program determines the state of the user's IP address from a databse of IPs
# We used this database when web scraping the data from http://whatsmyip.com stopped working
# because we sent too many requests

#create second database cursor for updating the records 
import DatabaseClass

#create database connection
db=DatabaseClass.Database()

#get a subset of records where the state has not yet been determined 
rows=db.read("select pkey, userIP from logs where state is null order by pkey desc limit 100000")

count=0
for row in rows:
    count += 1    
    getState=db.read("select city from ip_addresses where %s >=startip and %s <=endip order by startip desc limit 1",(row[1], row[1]), False)

    if getState==None:    
        state="unknown"
    else:
        state=getState[0]
      
    print count, row[0],row[1],state
    
    db.execute("update logs set state=%s where pkey=%s", (state, row[0]))    

print count, "records updated"
db.close()
