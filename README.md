# map_generator
generates a map showing markers on from a csv. May be at some point go into Pykell

There are basically two tools in this repo.

## generate_map.py

A quick and dirty script which adds markers from a csv to a map using folium

## generate_map_google_sheets.py

A bit a more sophisticated approach. It generates a map from a google sheets documents (needs some credential stuff, i just made this python first steps stuff to set it up), geocodes the adresses from that sheets document and uploads the generated html file to a ftp.

Needs to  be configured using a settings.json.

## License

do what ever the fuck you want. exept closing it and sue me. have some friends from Sicilia... 
