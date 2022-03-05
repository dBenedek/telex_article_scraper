#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 21:02:38 2022

@author: dbenedek
"""

###############################################################################
# Load packages:

import os
import json
from glob import glob
import re
from datetime import datetime
import plotly.express as px
import pandas as pd
import plotly.io as pio

###############################################################################
# Functions:

def list_json_files(path):
    """
    Lists the JSON files in path.
    
    Parameters
    ----------
    path : string
        Path to the JSON files.
        
    Returns
    -------
    json_files : list
        JSON files list.
    """
    json_files = [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.json'))]
    json_files.sort(key=lambda x: os.path.getmtime(x))
    return json_files

def get_top10_words(json_files):
    """
    Returns the top 10 most frequent words (at time point 0) for each 
    time point.
    
    Parameters
    ----------
    json_files : list
        Contains the JSON files' path in date order.

    Returns
    -------
    jsons_data : pandas dataframe
        Pandas dataframe with the word frequencies.
    """
    with open(json_files[0]) as json_file:
        file_01 = json.load(json_file)
    top10_words = list(file_01.keys())[-10:][::-1]
    jsons_data = pd.DataFrame(columns=top10_words)
    
    for index, js in enumerate(json_files):
        with open(os.path.join(js)) as json_file:
            json_text = json.load(json_file)
            
            count_all_words = sum(list(file_01.values()))
            
            for i in range(len(top10_words)):
                try:
                    globals()['top'+str(i+1)] = json_text[top10_words[i]]/count_all_words*100
                except KeyError:
                    globals()['top'+str(i+1)] = 0
            
            jsons_data.loc[index] = [top1, top2, top3, top4, top5,
                                     top6, top7, top8, top9, top10]
    jsons_data.index = [datetime.strptime(re.sub('\.json', '', 
                                                 re.sub('.*wordfreq_', '', w)), 
                                          '%Y_%m_%d_%H_%M_%S') for w in json_files]
    return jsons_data

def transform_data(jsons_data):
    """
    Transforms pandas dataframe to long format, approporiate for plotting.
    
    Parameters
    ----------
    jsons_data : pandas dataframe
        Contains the word frequencies per time point.

    Returns
    -------
    jsons_data_long : pandas dataframe
        Contains the word frequencies per date in a long format.
    """
    jsons_data_long = pd.DataFrame.transpose(jsons_data)
    jsons_data_long['word'] = jsons_data_long.index
    jsons_data_long = pd.melt(jsons_data_long, id_vars = ['word'], 
                              value_vars = list(jsons_data_long.columns[:-1]))
    jsons_data_long.columns = ['Word', 'Date', 'Percentage']
    jsons_data_long = jsons_data_long.sort_values(by = 'Date')
    return jsons_data_long

def plot_wordfreq(data):
    """
    Creates plotly line plot with word frequencies.
    
    Parameters
    ----------
    data : pandas dataframe
        Contains the word frequencies per date.

    Returns
    -------
    None.
    """
    fig = px.line(data, x='Date', y='Percentage', 
              color='Word', markers=True,
              title='Absolute frequency of the 10 most frequent words (at time point 0)',
              labels={"Percentage": "Frequency [%]"})
    fig.update_layout(yaxis_range=[0, max(data['Percentage'])])
    pio.renderers.default='browser'
    fig.show()

###############################################################################
# Run analysis:

jsons_data = list_json_files('/home/dbenedek/telex_data')
word_freq = get_top10_words(jsons_data)
word_freq_transformed = transform_data(word_freq)
plot_wordfreq(word_freq_transformed)

###############################################################################












