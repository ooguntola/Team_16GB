# This program reads and parses all of the log files in a directory
# It stores unique visits to a database (unique IP address and user agent)
# It also calculates hourly total page loads and saves the totals to a database table

import os
import sys
import datetime

#create second database cursor for updating the records 
import DatabaseClass

#create database connection
db=DatabaseClass.Database()

try:
    #create list to hold hourly counts of activity
    hourCount=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    #Count only UNIQUE visitors
    #create dictionary to hold processed unique visitors
    IPs={}  
    
    fileCount=0
    sourcePath="c:\\temp\\MSA8010\\"
    lst = os.listdir(sourcePath)
    
    #loop through all files in the directory
    for sourceFile in lst:
        print sourceFile
        sourceFilePath=sourcePath+sourceFile
        if os.path.isdir(sourceFilePath):       #skip subdirectories
            continue
      
        print "Processing",sourceFile
        f = open(sourceFilePath, 'r')           #open the file
        fileCount += 1

        #keep counts of lines processed        
        count=0
        skipped=0       #skip over duplicates
        inserted=0      #number of inserts into the database

        #initialize list of hours in a day to hold activity during that hour        
        for hr in range(0,24):
            hourCount[hr]=0
            
        while True:
            line=f.readline()
            if line =='':       #break on end of file
                break
            count += 1          #line count
    
            if count %10000 == 0:
                print "COUNT=",count
    
            if line[0] == '#':  #skip comment lines
                continue
        
            d=line.split()      #log file fields are space delimited
            
            hour=int(d[1][0:2])     #record hourly activity count
            hourCount[hour] += 1
            
            
            #we want only unique vistors
            #record entries from the same IP and same user address only once 
            #create unique key from user's IP address and user agent string
            uniqueVisitor = d[8]+d[9]   
            if uniqueVisitor in IPs:
                #print IPs
                #print d[8],"exists. Skipping"
                skipped += 1
                continue

            #cur.execute("""INSERT INTO logs (LogDate,LogTime,UserIP,UserAgent,SourceFile)
            #            VALUES (%s,%s,%s,%s,%s)""", \
            #            (d[0],d[1],d[8],d[9],sourceFile))
            
            inserted += 1
            IPs[uniqueVisitor] = "1"    

        #determine day of week for this log file. Mon=0, Sun=6
        year, month, day = (int(x) for x in d[0].split('-'))    
        dow = datetime.date(year, month, day).weekday()
        
        #record hourly counts for this day
        for hr in range(0, 24):
            if hr < 10 :
                hour = '0'+str(hr)
            else:
                hour = str(hr)                
            db.execute("""INSERT INTO activity VALUES (%s,%s,%s,%s)""", (d[0],dow,hour,hourCount[hr]))
        
        f.close()       #close file
        
        print "Processed", count, "log entries"
        print skipped," duplicates were skipped"
        print inserted,"entries were inserted into the database"
        
    
except IOError:
    print 'Error accessing files'
    sys.exit(1)

finally:

    db.close()
    
    print fileCount, "files were processed"
