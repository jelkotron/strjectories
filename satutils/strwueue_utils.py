from geopy import geocoders

def location_query(input):
    gn = geocoders.Nominatim(user_agent="my_App")
    output = gn.geocode(input, exactly_one=False)
    return output

