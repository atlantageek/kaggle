from os import listdir
from os.path import isfile, join

import sys
import gc
import csv
import math
import heapq
import time
import datetime
import string

import numpy

def convert_to_polar(coords1, coords2):
    dx = coords2[0] - coords1[0]
    dy = coords2[1] - coords1[1]

    r = (dx ** 2 + dy ** 2) ** 0.5

    if r == 0.0:
        theta = None
    elif dx == 0.0:
        sign = 1.0 if dy >= 0.0 else -1.0
        theta = sign * math.pi / 2.0
    else:
        theta = math.atan(dy / dx)

    return (r, theta)

class Driver:
    def __init__(self, path):
        self.path = path
        self.driver_id = path.split('/')[-1]
        self.files = [fname for fname in listdir(path) if isfile(join(path, fname))]
        self.trips = []
        self.trips_polar = []
        self._load_trips()
        print "Loaded driver %s with %d trips" % (self.driver_id, len(self.trips))

    def _load_trips(self):
        for fname in self.files:
            with open(join(self.path, fname), 'rb') as f:
                tripf = csv.reader(f)
                tripf.next()  # header row
                coords = [(float(row[0]), float(row[1])) for row in tripf]

            self.trips.append(numpy.array(coords))

            coords_polar = []
            for i in xrange(len(coords) - 1):
                pcoords = convert_to_polar(coords[i], coords[i + 1])

                if pcoords[1] is None and len(coords_polar) > 0:
                    pcoords = (pcoords[0], coords_polar[i - 1][1])

                coords_polar.append(pcoords)

            self.trips_polar.append(numpy.array(coords_polar))

    def distance_traveled(self, trip_idx):
        return sum((r[0] for r in self.trips_polar[trip_idx]))

    def trip_time(self, trip_idx):
        return len(self.trips[trip_idx])

    def average_distance_traveled(self):
        total_distance = sum((self.distance_traveled(i) for i in xrange(len(self.trips))))
        return total_distance / float(len(self.trips))

    def average_time_traveling(self):
        total_time = sum((len(trip) for trip in self.trips))
        return total_time / float(len(self.trips))

    def summary_stats(self):
        trip_times = []
        trip_distances = []

        ttrips = numpy.array([(len(self.trips[i]), self.distance_traveled(i)) for i in xrange(len(self.trips))])
        mean_time, mean_distance = numpy.mean(ttrips, axis = 0)
        median_time, median_distance = numpy.median(ttrips, axis = 0)
        min_time, min_distance = numpy.min(ttrips, axis = 0)
        max_time, max_distance = numpy.max(ttrips, axis = 0)

        return [self.driver_id, mean_distance, mean_time, max_distance, median_distance, min_distance, max_time, median_time, min_time]


    def build_features(self, trip):
        features = {}
        features[1] = 0.0 # average acceleration/deceleration
        features[2] = 0.0 # average


input_path = sys.argv[1]
driver_paths = [join(input_path, dirname) for dirname in listdir(input_path) if not isfile(join(input_path, dirname))]
drivers = [Driver(path) for path in driver_paths]

with open("driver_stats.csv", 'wb') as f:
    tripf = csv.writer(f)
    tripf.writerow(['DriverId', 'MeanDistance', 'MeanTime', 'MaxDistance', 'MedianDistance', 'MinDistance', 'MaxTime', 'MedianTime', 'MinTime'])

    for driver in drivers:
        stats = driver.summary_stats()
        tripf.writerow(stats)
        print stats

print "loaded all drivers"
