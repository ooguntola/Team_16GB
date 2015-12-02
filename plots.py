import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import scipy.stats

#create second database cursor for updating the records 
import DatabaseClass

#create database connection
db=DatabaseClass.Database(True)

def createSeries(resultSet):
    #create dictionary to hold the data pairs {date:hits} in a database result set
    d={}
    for row in resultSet:
        d[row[0]] = row[1]
    return pd.Series(d)
    
#create time series plot of unique user visits per day
#get a subset of records where the state has not yet been determined 
rows=db.read("select logdate, sum(hits) as hits from activity group by logdate order by logdate")

s=createSeries(rows)
s.plot()
print s.describe()

#create time series plot of unique visitors per browser type per day
dfData={}

rows=db.read("select logdate, count(browseros) from logs where browseros='Android' group by logdate,browseros order by logdate")
dfData['Android'] = createSeries(rows)

rows=db.read("select logdate, count(browseros) from logs where browseros='iOS' group by logdate,browseros order by logdate")
dfData['iOS'] = createSeries(rows)

rows=db.read("select logdate, count(browseros) from logs where browseros='Windows Phone' group by logdate,browseros order by logdate")
dfData['Windows Phone'] = createSeries(rows)

df=pd.DataFrame(dfData)
df=df.fillna(value=0)       #replace missing data with 0
print df
print df.describe()
#df.plot()


#Mobile user analysis
#create time series plot of unique visitors per browser type per month
dfData={}

rows=db.read("select date_part('week',logdate) as week, count(browseros) from logs where browseros='Android' group by date_part('week',logdate),browseros order by date_part('week',logdate)")
dfData['Android'] = createSeries(rows)

rows=db.read("select date_part('week',logdate) as week, count(browseros) from logs where browseros='iOS' group by date_part('week',logdate),browseros order by date_part('week',logdate)")
dfData['iOS'] = createSeries(rows)

rows=db.read("select date_part('week',logdate) as week, count(browseros) from logs where browseros='Windows Phone' group by date_part('week',logdate),browseros order by date_part('week',logdate)")
dfData['Windows_Phone'] = createSeries(rows)

rows=db.read("select date_part('week',logdate) as week, count(browseros) from logs where browseros in ('iOS','Android','Windows Phone') group by date_part('week',logdate) order by date_part('week',logdate)")
allMobile=rows      #save data for linear regression

rows=db.read("select date_part('week',logdate) as week, count(browseros) from logs group by date_part('week',logdate) order by date_part('week',logdate)")
dfData['All_Visitors'] = createSeries(rows)
allTraffic=rows     #save data for linear regression

#sum all mobile traffic counts
dfData['Mobile_Total'] =dfData['Android']+dfData['iOS']+dfData['Windows_Phone']


df=pd.DataFrame(dfData)
df=df.fillna(value=0)       #replace missing data with 0
print df.describe()
df.plot(); 


#day of week analysis unsing dataFrame JOIN
rows=db.read("select dayofweek,sum(hits) from activity group by dayofweek")
dow=createSeries(rows)
dowDF=pd.DataFrame(dow, columns=["Unique_Visitors"])

#create labels for day of week values and join the data frames
days=['Mon','Tues','Wed','Thurs','Fri','Sat','Sun']
daysDF=pd.DataFrame(days, columns=["Day"])

uniqueVisitorDays = dowDF.join(daysDF)  #JOIN two data frames
uniqueVisitorDays=uniqueVisitorDays.sort_values("Unique_Visitors", ascending=0)
print uniqueVisitorDays

#create labels
labels=[]
fractions=[]
for i in range(7):
    print i
    j=i+1
    labels.append(uniqueVisitorDays[i:j].Day.item())

#generate pie chart
uniqueVisitorDays.plot(kind="pie", autopct='%.2f%%', subplots=True, labels=labels, \
        colors=('g','r','b','m','c','y','w'))


#linear regession to find best fit line for all visitors
y=[allTraffic[i][1] for i in range(len(allTraffic))]
x=[allTraffic[i][0] for i in range(len(allTraffic))]

slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x,y)
print
print "All Visitors"
print "slope=", slope
print "intercept=", intercept
print "R-squared=", r_value**2, "standard error=",std_err


#linear regession to find best fit line for mobile users
y=[allMobile[i][1] for i in range(len(allMobile))]
x=[allMobile[i][0] for i in range(len(allMobile))]

slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x,y)
print
print "All Mobile"
print "slope=", slope
print "intercept=", intercept
print "R-squared=", r_value**2, "standard error=",std_err


#Create U.S> map of user activity from IP address locations
#matplotlib inline
from collections import defaultdict
import json

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from matplotlib import rcParams
import matplotlib.cm as cm
import matplotlib as mpl

#state map of users
states_abbrev = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

#adapted from  https://github.com/dataiap/dataiap/blob/master/resources/util/map_util.py
#load in state geometry
state2poly = defaultdict(list)

data = json.load(file("us-states.json"))

for f in data['features']:
    state = states_abbrev[f['abbrev']]
    geo = f['geometry']
    if geo['type'] == 'Polygon':
        for coords in geo['coordinates']:
            state2poly[state].append(coords)
    elif geo['type'] == 'MultiPolygon':
        for polygon in geo['coordinates']:
            state2poly[state].extend(polygon)

# Look at this link that describes the * and ** for Python arguments
# https://docs.python.org/dev/tutorial/controlflow.html#more-on-defining-functions
# In brief, * and ** for accepting arbitrary number of arguments. * as tuples and ** as dictionary 
            
def draw_state(plot, stateid, **kwargs):
    for polygon in state2poly[stateid]:
        xs, ys = zip(*polygon)
        plot.fill(xs, ys, **kwargs)


def make_map(states, label):
    fig = plt.figure(figsize=(12, 9))
    ax = plt.gca()

    #cmap = cm.binary
    cmap = cm.Reds
    vmin, vmax = 0, states.max().item()//1000
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    
    for state in states_abbrev.values():
        color = cmap(norm(states.ix[state].item()//1000))
        draw_state(ax, state, color = color, ec='k')

        
    #add an inset colorbar
    ax1 = fig.add_axes([0.45, 0.70, 0.4, 0.02])    
    #cb1=mpl.colorbar.ColorbarBase(ax1, cmap=cmap, norm=norm, orientation='horizontal')
    ax1.set_title(label)
    #remove_border(ax, left=False, bottom=False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-180, -60)
    ax.set_ylim(15, 75)
    return ax

rows=db.read("select trim(state),count(state) as unique_visitors from logs group by state order by state")
stateDataSeries=createSeries(rows)
statesDF=pd.DataFrame(stateDataSeries)
make_map(statesDF,"Unique Visitor Count by State (1,000's)")

db.close()