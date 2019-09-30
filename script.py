# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 06:19:44 2019

@author: ethan
"""

import numpy as np
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as td
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

def loadComments(n = 10):
    url = 'https://api.pushshift.io/reddit/search/comment/'
    params = '?q=&subreddit=economics&size=500&fields=body,author,created_utc'
    response = urllib.request.urlopen(url + params)
    data = json.loads(response.read())
    df = pd.DataFrame(data['data']).sort_index()
    
    for i in range(10):
        last = df.loc[df.index[-1], 'created_utc']
        params = '?q=&subreddit=economics&size=500&before={}&fields=body,author,created_utc'.format(last)
        response = urllib.request.urlopen(url + params)
        data = json.loads(response.read())
        df2 = pd.DataFrame(data['data']).sort_index()
        df = df.append(df2, True)
    df.to_pickle('data/DataBase.pkl')
    return df
def makeHist(data, color, p,top = 800, bins = 50):
    hist, edges = np.histogram(data, density=True, bins=bins, 
                               range = (df['wordCount'].min(),df['wordCount'].max()))
    


    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
           fill_color=color, line_color="white", alpha = 1)

    return p
def findmax(datas, bins = 50):
    hists = []
    for data in datas:
        hist, edges = np.histogram(data, density=True, bins=bins,
                                   range = (df['T10YIE'].min(),df['T10YIE'] .max()))
        hists.append(hist)
    return max(hist)


#df = loadComments()
#
#df['wordCount'] = df['body'].apply(lambda x: len(x.split()))
#print('Comment length - Mean: {} Median: {}'.format(df['wordCount'].mean(),df['wordCount'].median()))
#
#output_file('imgs\hist.html')
#p = figure(width = 1000,
#           height = 700,
#           title= '/r/Economics Comment Length: last 5,500 comments',
#           x_axis_label = 'Word Count',
#           y_axis_label = 'Density')
#
#med = df['wordCount'].median()
#hist, edges = np.histogram(df['wordCount'], density=True, bins='auto')
#
#p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
#       fill_color='blue', line_color="white", line_width = .25)
#top = max(hist)
#p.line([med,med],[0,top],line_dash = 'dashed', line_width = 2, color = 'black', 
#       legend = 'Median: {}'.format(med))
#
#p.y_range.start = 0
#p.y_range.end = top
#p.xgrid.grid_line_color = None
#p.ygrid.grid_line_color = None
#p.legend.location = 'top_right'
#show(p)


url = 'https://api.pushshift.io/reddit/search/submission/'
params = '?q=&subreddit=economics&size=500&fields=num_comments'
response = urllib.request.urlopen(url + params)
data = json.loads(response.read())
df = pd.DataFrame(data['data']).sort_index()

df = df.sort_values('num_comments')
df['cumsum'] = df['num_comments'].cumsum()
df['gini'] = df['cumsum']/df['num_comments'].sum()
output_file('imgs/' + str(dt.now())[:10]+ "_ginic.html")

p = figure(width = 700, height = 700,
           title="/r/Economics Lorentz Curves: Last 500 Submissions" ,
           x_axis_label = 'Cumulative Comments', 
           y_axis_label = 'Cumulative Share of Comments', y_range = (0,1), x_range = (1,0))
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.xaxis.formatter=NumeralTickFormatter(format="0%")
p.yaxis.formatter=NumeralTickFormatter(format="0%")
#p.line(xrng,[0,0], color = 'black')
#p.line([0,0],yrng, color = 'black')

def ginicalc(ser):
    tar = np.linspace(0,1,num = ser.size)
    diff = (tar - ser)/ser.size
    print(diff)
    return diff.sum()/.50
p.line(np.linspace(0,1,num = df['gini'].size), df['gini'], 
       legend = 'Gini Coefficient: {:.4f}'.format(ginicalc(df['gini'])),
       color = 'blue')
#show(p)
output_file('imgs/' + str(dt.now())[:10]+ "_bars.html")
p = figure(x_range = (0,100), plot_width = 1256, 
           title="/r/Economics Submission Comment Share", 
           x_axis_label = 'Rank', y_axis_label = 'Share of Comments')

p.vbar(x = range(100),color = 'blue', width = .9, 
       top = df.loc[df.index[500:400:-1],'num_comments']/df['num_comments'].sum())
p.xgrid.grid_line_color = None
p.y_range.start = 0


p.yaxis.formatter=NumeralTickFormatter(format="0.0%")
show(p)
print('done')

















