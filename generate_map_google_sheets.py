#!/usr/bin/env python3
# coding: utf-8
import re
import os
import ftplib
import time
from pprint import pprint

# google drive imports 
import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# folium imports
import folium
from folium.plugins import FloatImage
from folium.plugins import MarkerCluster
from branca.element import *

# Geocoding
from geopy.geocoders import Nominatim
geolocator = Nominatim()

OUTPUT_FILE = 'index.html'
LEGEND_IMG = 'legend.png'

MAP_STYLE = ''
MAP_ZOOM = 10
MAP_CENTER = [0.0,0.0]


ICONS = {'werkstatt': ['fa', 'wrench'], 'laden': ['fa', 'money'], 'lebensmittel': ['fa', 'shopping-basket'], 'elektronik': ['fa', 'laptop'],
         'hackerspace': ['fa', 'microchip'], 'holzwerkstatt': ['fa', 'tree'], 'bastelmaterial': ['fa', 'magnet'], 'metallwerkstatt': ['fa', 'cog'],'event':['fa','calendar'],'velowerkstatt': ['fa','bicycle']}
VERSIONS = {'bootstrap/3.2.0': 'bootstrap/4.0.0-beta.2',
            'font-awesome/4.6.3': 'font-awesome/4.7.0'}

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.
# Do
SCOPES = 'scope '
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'app name'
FILE_ID = 'your file id'

# FTP parameters 
FTP_SERVER = 'your-ftp-server.com'
FTP_USER = 'username'
FTP_PASSWD = 'password'


def read_settings():
    global MAP_CENTER, MAP_ZOOM, MAP_STYLE
    global FTP_SERVER, FTP_USER, FTP_PASSWD
    global OUTPUT_FILE, LEGEND_IMG
    global SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME, FILE_ID

    try:
        json_data=open('settings.json').read()
    except FileNotFoundError:
        print('Please provide a settings.json file')
        quit()
    data = json.loads(json_data)
    
    MAP_CENTER = data['map']['center']
    MAP_ZOOM = data['map']['zoom']
    MAP_STYLE = data['map']['style']
    FTP_SERVER = data['ftp']['server']
    FTP_PASSWD = data['ftp']['passwd']
    FTP_USER  = data['ftp']['user']
    OUTPUT_FILE = data['output_filename']
    LEGEND_IMG = data['legend_img']
    SCOPES = data['googleapi']['scopes']
    CLIENT_SECRET_FILE = data['googleapi']['client_secret_file']
    APPLICATION_NAME = data['googleapi']['application_name']
    FILE_ID = data['googleapi']['file_id']


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


# Add markers
def add_marker(lat, lon, popup, markertype, col='green'):
    global marker_cluster
    try:
        folium.Marker(
            location=[float(lat), float(lon)],
            popup=popup,
            icon=folium.Icon(icon=markertype[1], color=col, prefix=markertype[0],
            )
        ).add_to(marker_cluster)
    except ValueError:
        pass

# Fix bootstrap and font awesome versions
def fix_versions(htmlfile=OUTPUT_FILE  ):
    for tool in VERSIONS.keys():
        replace(htmlfile, tool, VERSIONS[tool])

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


def ftp_upload(file,server,folder,username,password): 
    with open(file,'rb') as f:
        print('Conneting as {} to {}'.format(FTP_USER,FTP_SERVER))
        session = ftplib.FTP(server,username,password)
        ftp_cmd = 'STOR ' + folder + '/' + file
        print(ftp_cmd)
        session.storlines(ftp_cmd,f)
        session.quit()


def main():
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    read_settings()

    global marker_cluster

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = FILE_ID
    rangeName = 'Sheet1!A2:H'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])
    # Initialize map
    print('Generating map at {}, zoomlevel: {}, style {}'.format(MAP_CENTER,MAP_ZOOM,MAP_STYLE))
    m = folium.Map(location=MAP_CENTER,
                   zoom_start=MAP_ZOOM,
                   tiles=MAP_STYLE
                   )

    marker_cluster = MarkerCluster().add_to(m)

    if not values:
        print('No data found.')
    else:
        for row in values:
            coords = geolocator.geocode(row[1])
            popup = '<a target="_blank" href="{}"><b>{}</b></a><br/>{}<br/>{}<br/>{}'.format(
                row[4], row[0], row[5], row[1], row[6])
            try:
                markertype = ICONS[row[7].lower()]
            except KeyError:
                markertype = ['fa', 'asterisk']
            print('Adding marker for {} at {}, {}'.format(row[0],coords.latitude, coords.longitude))
            add_marker(coords.latitude, coords.longitude, popup, markertype)
            

    # Add Logo
    FloatImage(LEGEND_IMG, bottom=1, left=1).add_to(m)

    # Draw Map
    m.save(OUTPUT_FILE )
    fix_versions()

    ftp_upload(OUTPUT_FILE ,FTP_SERVER,'www',FTP_USER,FTP_PASSWD)


if __name__ == '__main__':
    main()







