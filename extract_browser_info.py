# This program uses regular expressions to determine the operating system and
# browser type from the user agent string reported in the logs

import re

#create second database cursor for updating the records 
import DatabaseClass

#create database connection
db=DatabaseClass.Database()

#get a subset of records where the state has not yet been determined 
rows=db.read("select pkey, useragent from logs where browsername is null")

count=0
emptyCount=0

for row in rows:
    count += 1    
    #print count, row[0], row[1]

    os=''
    browser=''
    
    pkey=row[0]
    ua=row[1]
    
    match = re.search("MSIE.*?;", ua)   #Internet Explorer    
    if match:
        ver = match.group(0)
        ver = re.sub('MSIE.','', ver) 
        ver = re.sub(';','', ver)
        browser = 'IE '+ver
    else:
        match = re.search("Trident.*?;", ua)    #also Internet Explorer
        if match:
            ver = match.group(0)
            ver = re.sub('Trident.','', ver) 
            ver = re.sub(';','', ver)
            browser = 'IE '+ver
        
        else:            
            match = re.search("Firefox",ua)      
            if match:
                browser = 'Firefox'
            else:
                match = re.search("Chrome",ua)      
                if match:
                    browser='Chrome'
                else:
                    match = re.search("Safari",ua)      
                    if match:
                        browser='Safari'
                    else:
                        browser='other'
                    
                
            
    #look for Windows - string may end with either ; or )
    match = re.search("Windows.NT.*?[;)]", ua)  
    if match:
        #print match.group(0)
        
        #Determine Windows version
        ver = match.group(0)
        ver = re.sub('Windows.','', ver) 
        ver = re.sub('[;)]','', ver)
        
        os='Windows '
        if ver == 'NT+6.1': 
            os += '7'
        elif ver == 'NT+6.2' or ver == 'NT+6.3':
            os += '8'
        elif ver == 'NT+6.0':
            os += 'Vista'
        elif ver == 'NT+10.0':
            os += '10'
        elif ver == 'NT+5.1' or ver == 'XP':
            os += 'XP'
        elif ver.startswith('Phone'):
            os += 'Phone'
    
    else:
        match = re.search("Android", ua)  
        if match:
            os='Android'
            
        else:
            match1 = re.search("iPhone", ua)
            match2 = re.search("iPad", ua)

            #Darwin is also used for iOS and Mac desktops    
            darwin = re.search("Darwin", ua)
            if darwin:
                browser='Safari'
            mobileSafari =re.search("MobileSafari", ua)
            if mobileSafari:
                browser='Safari'
                
            if match1 or match2 or (darwin and mobileSafari):
                os='iOS'
                if browser=='':
                    browser = 'Safari'
            else:
                match = re.search("Macintosh", ua)
                if match or (darwin and not mobileSafari):
                    os = 'Mac Desktop'
                else:
                    os = 'other'
                
    #print ua
    if browser=='' or os=='':
        emptyCount += 1
        print emptyCount, pkey, "b=",browser, "os=",os, ua   
    
    db.execute("update logs set browsername=%s, browseros=%s where pkey=%s", (browser, os, pkey))    
            
print "Done.", count, "records were processed.", emptyCount, "could not be processed."  
db.close()
              
