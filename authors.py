# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 07:17:38 2019

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
import math

from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import NumeralTickFormatter
from bokeh.palettes import Inferno256 as colors
creds = pd.read_csv('credentials.csv').T.to_dict()[0]
reddit = praw.Reddit(**creds)

df = pd.read_pickle('data\DataBase.pkl')
df['ones'] = 1

g = df.groupby('author')
agg = g.agg(np.sum)['ones'].sort_values(ascending = False)[1:50]
print(agg)
agg = agg.reset_index()
ydata = agg['ones']/agg['ones'].sum()
output_file('imgs/' + str(dt.now())[:10]+ "_bars.html")
p = figure(x_range = agg['author'], plot_width = 1256, 
           title="/r/Economics User Comment Share", 
           x_axis_label = 'User', y_axis_label = 'Share of Comments')

p.vbar(x = agg['author'],color = 'blue', width = .9, 
       top = ydata)
p.xgrid.grid_line_color = None
p.y_range.start = 0
p.xaxis.major_label_orientation = math.pi/4

p.yaxis.formatter=NumeralTickFormatter(format="0.0%")
show(p)
print('done')
