#!/usr/bin/env python3
# coding: utf-8
import folium
import csv
import re

from folium.plugins import FloatImage
from folium.plugins import MarkerCluster

from branca.element import *

out_filename = 'index.html'
legend = 'logo1.png'

icons = {'werkstatt': ['fa', 'wrench'], 'laden': ['fa', 'money'], 'lebensmittel': ['fa', 'shopping-basket'], 'elektronik': ['fa', 'laptop'],
         'hackerspace': ['fa', 'microchip'], 'holzwerkstatt': ['fa', 'tree'], 'bastelmaterial': ['fa', 'magnet'], 'metallwerkstatt': ['fa', 'cog'],'event':['fa','calendar'     ]}
versions = {'bootstrap/3.2.0': 'bootstrap/4.0.0-beta.2',
            'font-awesome/4.6.3': 'font-awesome/4.7.0'}

map_center = [47.3686498, 8.5391825]


# CSV handling
def read_csv_file(file):
    try:
        f = open(file, 'rt')
        return csv.reader(f)
    except FileNotFoundError:
        print(file + ': File not found')
    except IndexError:
        print(file + ': File not formated well')


def parse_csv(reader):
    global header
    header = next(reader)
    markers = []
    for row in reader:
        mrk = parse_row(row)
        add_marker(mrk[0], mrk[1], mrk[2], mrk[3])


def parse_row(row):
    lat = row[2]
    lon = row[3]
    popup = '<a target="_blank" href="{}"><b>{}</b></a><br/>{}<br/>{}<br/>{}'.format(
        row[4], row[0], row[5], row[1], row[6])
    try:
        markertype = icons[row[7].lower()]
    except KeyError:
        markertype = ['fa', 'asterisk']
    return (lat, lon, popup, markertype)


# Add markers
def add_marker(lat, lon, popup, markertype, col='green'):
    folium.Marker(
        location=[float(lat), float(lon)],
        popup=popup,
        icon=folium.Icon(icon=markertype[1], color=col, prefix=markertype[0],
        )
    ).add_to(marker_cluster)


# Fix bootstrap and font awesome versions
def fix_versions(htmlfile=out_filename):
    for tool in versions.keys():
        replace(htmlfile, tool, versions[tool])

# Add headers


def add_header():
    pass


# Replace stuff in files
def replace(file, pattern, subst):
    # Read contents from file as a single string
    file_handle = open(file, 'r')
    file_string = file_handle.read()
    file_handle.close()

    # Use RE package to allow for replacement (also allowing for (multiline)
    # REGEX)
    file_string = (re.sub(pattern, subst, file_string))

    # Write contents to file.
    # Using mode 'w' truncates the file.
    file_handle = open(file, 'w')
    file_handle.write(file_string)
    file_handle.close()


# Initialize map
m = folium.Map(location=map_center,
               zoom_start=12,
               tiles='Stamen Toner',
               )

marker_cluster = MarkerCluster().add_to(m)


reader = read_csv_file('data.csv')
parse_csv(reader)


# Add Logo
FloatImage(legend, bottom=1, left=1).add_to(m)


# Draw Map
m.save(out_filename)
fix_versions()
