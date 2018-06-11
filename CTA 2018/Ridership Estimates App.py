#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 13:42:46 2018

@author: alexdamisch
"""

### Inspired by https://plot.ly/pandas/scatter-plots-on-maps/
### and an internal CTA app by Matthew Hamilton, CTA employee

import pandas
import numpy
import plotly
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode
import os

# This plots offline
init_notebook_mode()


color_formatting = {
    'RED': 'Red',
    'BLUE': 'Blue',
    'G': 'Green',
    'BRN': 'Brown',
    'P': 'Purple',
    'Pexp': 'Purple',
    'Y': 'Yellow',
    'Pnk': 'Pink',
    'O': 'Orange',
}


# Line colors
def get_color(row):
    for k in color_formatting.keys():
        if row[k]:
            return color_formatting[k]

scl = [
    ["Red", "rgb(5, 10, 172)"],
    ["Blue", "rgb(40, 60, 190)"],
    ["Brown", "rgb(70, 100, 245)"],
    ["Purple", "rgb(90, 120, 245)"],
    ["Yellow", "rgb(106, 137, 247)"],
    ["Pink", "rgb(220, 220, 220)"]
]


# Reading in list of stations, removing duplicates
# List of stations was taken from Chicago Data Portal
def main():
    station_df=pandas.read_csv('https://raw.githubusercontent.com/adamisch/grad/master/CTA%202018/List%20of%20L%20Stops.csv')
    station_df['Lat'] = station_df['Location'].apply(lambda x: x.split(', ')[0][1:])
    station_df['Lon'] = station_df['Location'].apply(lambda x: x.split(', ')[1][:-1])
    station_df.drop_duplicates('STATION_DESCRIPTIVE_NAME', inplace=True)
    station_df.drop_duplicates('MAP_ID', inplace=True)
    station_df['Color'] = [get_color(station_df.iloc[x]) for x in range (0, len(station_df))]
    station_df.drop(station_df.columns[6:16], axis=1, inplace=True)
    return station_df


maindf = main()

# Queried from ridership estimates
rows=pandas.read_csv('https://raw.githubusercontent.com/adamisch/grad/master/CTA%202018/rows.csv')

# Station names to match
stations=pandas.read_csv('https://raw.githubusercontent.com/adamisch/grad/master/CTA%202018/stations.csv')

# Mapping ridership estimates to list of stations for IDs
rows['station_id'] = rows['facility_name'].map(stations.set_index('facility_name')['station_id'])+40000

# The main DF has the coordinates of the stations, and "rows" has the sizes
rows.sort_values(by="station_id", inplace=True)

# Mapping ridership estimates to list of stations for location, color
rows['Lat'] = rows['station_id'].map(maindf.set_index('MAP_ID')['Lat'])
rows['Lon'] = rows['station_id'].map(maindf.set_index('MAP_ID')['Lon'])
rows['Color'] = rows['station_id'].map(maindf.set_index('MAP_ID')['Color'])


def plotsize(step):
    test = rows[rows["datetime"] == step]
    minsize = min(test["sum"])
    maxsize = max(test["sum"])
# normalize to (5, 30) range for plotting
# Nothing special about (5, 30), it could certainly be tweaked
    sizes = [(item-minsize) / (maxsize-minsize) * (30 - 5) + 5 for item in test.iloc[:, 6]]
    return(sizes)


def plotlabel(step):
    test = rows[rows["datetime"] == step]
    lab = [str(test['facility_name'].iloc[i]+" "+str(round(test['sum'].iloc[i]))) for i in range(len(test))]
    return(lab)


def plotlat(step):
    test = rows[rows["datetime"] == step]
    return(test['Lat'])


def plotlon(step):
    test = rows[rows["datetime"] == step]
    return(test['Lon'])


def plotcolor(step):
    test = rows[rows["datetime"] == step]
    return(test['Color'])


# This has to be sorted so it can show up correctly on the sliders
times = numpy.sort(rows["datetime"].unique())

# Create data frame with different plot sizes/labels for each unique time value
data = [dict(
        visible=False,
        type="scattergeo",
        mode="markers",
        marker=dict(
            size=plotsize(step),
            opacity=0.8,
            reversescale=True,
            autocolorscale=False,
            line=dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            color=plotcolor(step)
            ),
        text=plotlabel(step),
        lat=plotlat(step),
        lon=plotlon(step)) for step in times]

# Set data visibility/sliders to first value
data[0]['visible'] = True

sliders = [{
    'active': 0,
    'currentvalue': {
        "prefix": "Time: "
    },
    'pad': {
        "t": 0
    },
    'steps': [{
        'method': 'restyle',
        'label': pandas.to_datetime(str(i)).strftime('%m/%d %H:%M'),
        'args': [
            'visible',
            [i == j for j in times]
        ]
    } for i in times]
}]

layout = dict(
    geo=dict(
        scope='north america',
        showland=True,
        landcolor="rgb(212, 212, 212)",
        subunitcolor="rgb(255, 255, 255)",
        countrycolor="rgb(255, 255, 255)",
        showlakes=True,
        lakecolor="rgb(255, 255, 255)",
        showsubunits=True,
        showcountries=True,
        resolution=50,
        projection=dict(
            type='conic conformal',
            rotation=dict(
                lon=-90
            )
        ),
        lonaxis=dict(
            showgrid=True,
            gridwidth=0.5,
            range=[-87.9, -87.5],
            dtick=5
        ),
        lataxis=dict(
            showgrid=True,
            gridwidth=0.5,
            range=[41.69, 42.1 ],
            dtick=5
        )
    ),
    sliders=sliders)

plotly.offline.plot({
    "data": data,
    'layout': layout
})
