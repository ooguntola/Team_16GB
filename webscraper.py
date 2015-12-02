# This program scrapes IP address locations from a web site http://whatsmyip.com
# It uses regular expressions to locate the state in the hmtl page that is returned
# There is a limit of 50 before the host locks us out.

import re
import urllib2 


#create second database cursor for updating the records 
import DatabaseClass

#create database connection
db=DatabaseClass.Database()

class CrawlIP:

    def getState(self, ip):
        host="http://whatismyipaddress.com/ip/"
        
        req = urllib2.Request(host+ip, headers={ 'User-Agent': 'Mozilla/5.0' })
        html = urllib2.urlopen(req).read()

        #print html
        
        #get string with any number of characters (using .*?) after State/region:</th></td>
        # .* means any char string and ? means non-greedy (stop at first match)
        match= re.search("State/Region:</th><td>.*?</td></tr>",html)        
        if match:
            loc = match.group(0)
            loc = re.sub('State/Region:</th><td>','',loc) 
            state = re.sub('</td></tr>','',loc)
        else:
            state = "Not Found"
        return state


demo=True

ip=CrawlIP()

if demo:
    ip1="131.96.210.58"
    ip2="66.249.79.84"
            
    print ip1, ip.getState(ip1)
    print ip2, ip.getState(ip2)
    count=2
    
else:    
    rows=db.read("select pkey, userIP from logs where state is null limit 100")
    
    count=0
    for row in rows:
        count += 1
        state=ip.getState(row[1])
        print count, row[0], row[1], state
        db.execute("update logs set state=%s where pkey=%s", (state, row[0]))    

print "Done.", count, "records updated"
db.close()

