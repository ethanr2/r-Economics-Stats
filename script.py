# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 06:19:44 2019

@author: ethan
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta, timezone
import praw
import numpy as np
import pandas as pd
import json as js
import urllib, json


from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import NumeralTickFormatter
from bokeh.palettes import Inferno256 as colors
creds = pd.read_csv('credentials.csv').T.to_dict()[0]
reddit = praw.Reddit(**creds)

def loadComments(sub = 'Economics', n = 365):
    start= dt.now()
    url = 'https://api.pushshift.io/reddit/search/comment/'
    params = '?q=&subreddit={}&size=500&fields=author,body,created_utc'.format(sub)
    response = urllib.request.urlopen(url + params)
    data = json.loads(response.read())
    df = pd.DataFrame(data['data'])
    df['Time'] = df['created_utc'].apply(lambda x: dt.fromtimestamp(x))
    df.index = pd.DatetimeIndex(df['Time'])
    df = df.sort_index()
    last = df.loc[df.index[-1], 'Time']
    stop = dt.now() -  timedelta (days = n)
    print(stop, last)
    params = params + '&before={}'
    i = 500
    while last > stop:
        last = df['Time'].min()
        print('Last:', last)
        #print(last.timestamp(), url + params.format(int(last.timestamp())))
        response = urllib.request.urlopen(url + params.format(int(last.timestamp())))
        data = json.loads(response.read())
        df2 = pd.DataFrame(data['data'])
        df2['Time'] = df2['created_utc'].apply(lambda x: dt.fromtimestamp(x))
        df2.index = pd.DatetimeIndex(df2['Time'])
        df2 = df2.sort_index()
        df = df.append(df2, True)
        i = i + 500
        if i % 20000 == 0:
            df.to_pickle('data/sub_DataBase_{}.pkl'.format(i))
            df = df2
            
        print(dt.now() - start, i, last - stop)
              
    df.to_pickle('data/sub_DataBase_{}.pkl'.format(i))
    return df

# Don't use this unless the DataBase.pkl file gets messed up in some way.
def complieAllSubDBs():
    files = ['data/' + file for file in os.listdir('data') if file != 'DataBase.pkl']
    df = pd.read_pickle(files.pop())
    
    end = df['Time'].max()
    start = df['Time'].min()
                   
    for file in files:
        df2 = pd.read_pickle(file)
        df2 = df2.loc[(df2['Time'] > end) | (df2['Time'] < start), :]
        df = df.append(df2, ignore_index = True,sort=False).sort_values('Time')
        end = df['Time'].max()
        start = df['Time'].min()
        print( df['Time'].min(), df['Time'].max(), file)
        #break
    df.to_pickle('data/DataBase.pkl')
    return df

#df = loadComments(n = 365)
df = complieAllSubDBs()


def makeHist():    
    df['wordCount'] = df['body'].apply(lambda x: len(x.split()))
    print('Comment length - Mean: {} Median: {}'.format(df['wordCount'].mean(),df['wordCount'].median()))
    
    output_file('imgs\hist.html')
    p = figure(width = 1000,
               height = 700,
               title= '/r/Economics Comment Length: last 5,500 comments',
               x_axis_label = 'Word Count',
               y_axis_label = 'Density')
    
    med = df['wordCount'].median()
    hist, edges = np.histogram(df['wordCount'], density=True, bins='auto')
    
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
           fill_color='blue', line_color="white", line_width = .25)
    top = max(hist)
    p.line([med,med],[0,top],line_dash = 'dashed', line_width = 2, color = 'black', 
           legend = 'Median: {}'.format(med))
    
    p.y_range.start = 0
    p.y_range.end = top
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.legend.location = 'top_right'
    show(p)

df['word_count'] = df['body'].apply(lambda x: len(x.split()))
df.index = df['Time']
df = df.sort_index()
df['ave'] = df['word_count'].rolling("7d").mean()


xdata = df['Time']
ydata = df['ave']
xrng = (xdata.min(),xdata.max())
yrng = (0,ydata.max())



xdata = xdata.dropna()
ydata = ydata.dropna()



from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import NumeralTickFormatter
#from bokeh.palettes import Inferno256 as colors
from bokeh.models import SingleIntervalTicker, LinearAxis

output_file("imgs\wordcount_series.html")

p = figure(width = 1400, height = 700,
           title="/r/Economics Average Word Count" ,
           x_axis_label = 'Date', x_axis_type='datetime',
           y_axis_label = 'Word Count Per Comment', y_range = yrng, x_range = xrng)
p.xgrid.grid_line_color = None
#p.ygrid.grid_line_color = None

p.line(xrng,[0,0], color = 'black')
p.line([0,0],yrng, color = 'black')



#slope, intercept, r_value, p_value, std_err = stats.linregress(xdata, ydata)

p.line(xdata, df['ave'], 
       legend = '7 Day Moving Average', 
       color = 'deepskyblue')
#p.circle(xdata, df['word_count'], color = 'deepskyblue', size = 1)


p.xaxis[0].ticker.desired_num_ticks = 20

show(p)

#url = 'https://api.pushshift.io/reddit/search/submission/'
#params = '?q=&subreddit=economics&size=500&fields=num_comments'
#response = urllib.request.urlopen(url + params)
#data = json.loads(response.read())
#df = pd.DataFrame(data['data']).sort_index()
#
#df = df.sort_values('num_comments')
#df['cumsum'] = df['num_comments'].cumsum()
#df['gini'] = df['cumsum']/df['num_comments'].sum()
#output_file('imgs/' + str(dt.now())[:10]+ "_ginic.html")
#
#p = figure(width = 700, height = 700,
#           title="/r/Economics Lorentz Curves: Last 500 Submissions" ,
#           x_axis_label = 'Cumulative Comments', 
#           y_axis_label = 'Cumulative Share of Comments', y_range = (0,1), x_range = (1,0))
#p.xgrid.grid_line_color = None
#p.ygrid.grid_line_color = None
#p.xaxis.formatter=NumeralTickFormatter(format="0%")
#p.yaxis.formatter=NumeralTickFormatter(format="0%")
##p.line(xrng,[0,0], color = 'black')
##p.line([0,0],yrng, color = 'black')
#
#def ginicalc(ser):
#    tar = np.linspace(0,1,num = ser.size)
#    diff = (tar - ser)/ser.size
#    print(diff)
#    return diff.sum()/.50
#p.line(np.linspace(0,1,num = df['gini'].size), df['gini'], 
#       legend = 'Gini Coefficient: {:.4f}'.format(ginicalc(df['gini'])),
#       color = 'blue')
##show(p)
#output_file('imgs/' + str(dt.now())[:10]+ "_bars.html")
#p = figure(x_range = (0,100), plot_width = 1256, 
#           title="/r/Economics Submission Comment Share", 
#           x_axis_label = 'Rank', y_axis_label = 'Share of Comments')
#
#p.vbar(x = range(100),color = 'blue', width = .9, 
#       top = df.loc[df.index[500:400:-1],'num_comments']/df['num_comments'].sum())
#p.xgrid.grid_line_color = None
#p.y_range.start = 0
#
#
#p.yaxis.formatter=NumeralTickFormatter(format="0.0%")
#show(p)
#print('done')

















