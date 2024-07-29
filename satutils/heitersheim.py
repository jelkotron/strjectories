#!/home/schnollie/.venvs/strwueue/bin/python
from geopy import geocoders  

gn = geocoders.GeoNames("<random_username>")
heitersche = gn.geocode("Heitersheim", exactly_one=False)[0]