import matplotlib.pyplot as pyplot
from mpl_toolkits.basemap import Basemap
from matplotlib.widgets import TextBox
import random
import numpy


class Satellite(object):
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.velocity = 0

    def update():
        pass



# use ggplot style for more sophisiticated visuals
pyplot.style.use('ggplot')

DEFAULT_RADIUS = 100

places = {'Mexico City': (19.05, -99.366667),
          'London': (51.507222, -0.1275),
          'Sydney': (-33.859972, 151.211111),
          'Cape Town': (-33.925278, 18.423889),
          'Delhi': (28.61, 77.23),
          'Karlsruhe': (48.99987, 8.39414)
          }

network = [
           ('London', 'Delhi'),
           ('Mexico City', 'Sydney'),
           ('Cape Town', 'Karlsruhe')
           ]

karlsruhe = {
    'lat': 48.99987,
    'lon': 8.39414,
}

def live_plotter(x_vec, y1_data, line1, identifier='', pause_time = 0.2):
    if line1 == []:
        pyplot.ion() # allow dynamic plotting
        fig = pyplot.figure(figsize=(13,6))
        ax = fig.add_subplot(111)
        line1, = ax.plot(x_vec, y1_data, '-o', alpha=0.8) # variable for line to update (strange comma unpacks tuple)
        pyplot.ylabel('Y')
        pyplot.title('asasasa: {}'.format(identifier))
        pyplot.show()

    line1.set_ydata(y1_data)

    # adjust limits if new data goes out of bounds
    if numpy.min(y1_data) <= line1.axes.get_ylim()[0] or numpy.max(y1_data) >= line1.axes.get_ylim()[1]:
        pyplot.ylim([numpy.min(y1_data) - numpy.std(y1_data), numpy.max(y1_data) + numpy.std(y1_data)])

    pyplot.pause(pause_time)

    return line1

def submit(expression):
    print(expression)

def map_plotter():

    t_step = 0.2
    num_ticks = 0

    fig, ax = pyplot.subplots(figsize=(12,10))
    pyplot.title("STRWÜÜ")
    
    satellites = generate_points(10)

    map = Basemap(
        projection='merc',
        llcrnrlat=-80,urcrnrlat=80,
        llcrnrlon=-180,
        urcrnrlon=180,
        lat_ts=20,
        resolution='c'
        )
    
    map.drawcoastlines()
    map.fillcontinents(color='coral',lake_color='aqua')

    map.drawparallels(numpy.arange(-90, 90, 15))
    map.drawmeridians(numpy.arange(-180, 180, 30))
    map.drawmapboundary(fill_color='aqua') 

    

    # if len(satellites) > 0:
    #     pyplot.ion()

    for i in range(len(satellites)):
        sat = satellites[i]
        map.scatter(sat.lon, sat.lat, marker='X', color='g', zorder=5, latlon=True)

    # for origin, destination in network:
    #     lat0, lon0 = places[origin]
    #     lat1, lon1 = places[destination]
    #     line, = map.drawgreatcircle(lon0, lat0, lon1, lat1, lw=3)

    #     path = line.get_path()
    #     p_cut = numpy.where(numpy.abs(numpy.diff(path.vertices[:, 0])) > 200)[0]

    #     if p_cut.any:
    #         p_cut = p_cut[0]
    #         new_verts = numpy.concatenate(
    #             [
    #             path.vertices[:p_cut, :],
    #             [[numpy.nan, numpy.nan]],
    #             path.vertices[p_cut+1:, :] 
    #             ]
    #         )
    #         path.codes = None
    #         path.vertices = new_verts

    # for name, coords in places.items():
    #     map.scatter(coords[1],coords[0], marker='o', color='r', zorder=5, latlon=True)

    # axbox = fig.add_axes([0.1, 0.13, 0.8, 0.03])
    # bxbox = fig.add_axes([0.1, 0.09, 0.8, 0.03])
    # cxbox = fig.add_axes([0.1, 0.05, 0.8, 0.03])
    # dxbox = fig.add_axes([0.1, 0.01, 0.8, 0.03])
    

    # city_box = TextBox(axbox, "City:", textalignment="center")
    # city_box.on_submit(submit)
    # city_box.set_val("Karlsruhe")  # Trigger `submit` with the initial string.
    
    # lat_box = TextBox(bxbox, "Latitude:", textalignment="center")
    # lat_box.on_submit(submit)
    # lat_box.set_val(places["Karlsruhe"][0])  # Trigger `submit` with the initial string.
    
    # lon_box = TextBox(cxbox, "Longitude:", textalignment="center")
    # lon_box.on_submit(submit)
    # lon_box.set_val(places["Karlsruhe"][1])  # Trigger `submit` with the initial string.

    # lon_box = TextBox(dxbox, "Radius(m):", textalignment="center")
    # lon_box.on_submit(submit)
    # lon_box.set_val(DEFAULT_RADIUS)  # Trigger `submit` with the initial string.


    # fig.subplots_adjust(bottom=0.2)



    pyplot.show()
    
def generate_points(num_pts):
    min_lat, max_lat = -80, 80
    min_lon, max_lon = -180, 180
    
    points = []

    for i in range(num_pts):
        sat = Satellite(
            lat = random.uniform(min_lat, max_lat),
            lon = random.uniform(min_lon, max_lon)
            )
        points.append(sat)

    return points



















# class Canvas(object):
#     def __init__(self, lat=places['Karlsruhe'][0], lon=places['Karlsruhe'][1], radius=100.0):
#         self.lat = lat
#         self.lon = lon
#         self.center = [lat, lon]
#         self.radius = radius
       
#         print("Canvas initiated!")
    
