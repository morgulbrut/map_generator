#!/usr/bin/env python3
# coding: utf-8
import folium
import csv

icons = {'werkstatt':'wrench', 'laden':'credit-card'}


'''CSV handling'''
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
        add_marker(mrk[0],mrk[1],mrk[2],mrk[3])

def parse_row(row):
    lat = row[2]
    lon = row[3]
    popup = '<a target="_blank" href="{}"><b>{}</b></a><br/>{}<br/>{}'.format(row[4],row[0],row[5],row[6])
    markertype = icons[row[7].lower()]
    return (lat,lon,popup,markertype)
        
'''Add markers'''
def add_marker(lat,lon,popup,markertype,col='black'):
    folium.Marker(
        location=[float(lat),float(lon)],
        popup=popup,
        icon=folium.Icon(icon=markertype,color=col)
    ).add_to(m)

'''Initialize map'''
m = folium.Map(location=[47.3686498, 8.5391825],
               zoom_start=11,
               tiles='Stamen Toner',
)

reader = read_csv_file('data.csv')
parse_csv(reader)


'''Add icon'''
folium.Icon(
    icon=folium.Icon(icon='cloud')
).add_to(m)

m.save('map.html')
