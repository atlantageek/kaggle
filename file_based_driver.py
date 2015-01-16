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

    return [r, theta]

class Driver(object):
    def __init__(self, path):
        self.path = path
        self.driver_id = int(path.split('/')[-1])
        self.trip_ids = sorted([int(fname.split('.')[0]) for fname in listdir(path) if isfile(join(path, fname))])
        self.trips = []
        self.trips_polar = []
        self._load_trips()
        print "Loaded driver %s with %d trips" % (self.driver_id, len(self.trips))

    def _load_trips(self):
        rect_trips = []
        polar_trips = []
        self.files = []

        for trip_id in self.trip_ids:
            fname = join(self.path, "%d.csv" % (trip_id))
            self.files.append(fname)
            with open(fname, 'rb') as f:
                tripf = csv.reader(f)
                tripf.next()  # header row
                coords = [(float(row[0]), float(row[1])) for row in tripf]

            rect_trips.append(numpy.array(coords))

            coords_polar = [numpy.array((0.0, 0.0))]
            initial_theta = None
            for i in xrange(len(coords) - 1):
                r, theta = convert_to_polar(coords[i], coords[i + 1])

                if initial_theta is None:
                    initial_theta = theta or 0.0
                    pcoords = (r, 0.0)
                elif theta is None and len(coords_polar) > 0:
                    pcoords = (r, coords_polar[i - 1][1])
                else:
                    pcoords = (r, theta - initial_theta)

                coords_polar.append(numpy.array(pcoords))

            polar_trips.append(numpy.array(coords_polar))

        self.trips = numpy.array(rect_trips)
        self.trips_polar = numpy.array(polar_trips)

    def distance_traveled(self, trip_idx):
        return sum((r[0] for r in self.trips_polar[trip_idx]))

    def trip_time(self, trip_idx):
        return len(self.trips[trip_idx])

    def compute_accelerations(self):
        tmpary = []
        for trip in self.trips_polar:
            tmpary.append(numpy.diff(trip, axis = 0))

        # array of arrays of (velocity, angular_velocity)
        self.accelerations = numpy.array(tmpary)
        return self.accelerations

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

    def build_features(self, sample_size = 0.25):
        self.compute_accelerations()

        features = []

        for i in xrange(len(self.trips)):
            # IDEAS:
            # distance traveled, time of trip, mean velocity, mean acceleration, mean angular velocity, mean angular acceleration
            row_features = []
            row_features.append(self.distance_traveled(i))
            row_features.append(len(self.trips[i]))

            veloc_means = numpy.mean(self.trips_polar[i], axis = 0)
            row_features.append(veloc_means[0])
            row_features.append(veloc_means[1])

            accel_means = numpy.mean(self.accelerations[i], axis = 0)
            row_features.append(accel_means[0])
            row_features.append(accel_means[1])

            ratios = []
            for j in xrange(len(self.accelerations[i])):
                if self.accelerations[i][j][1] > math.pi / 16.0 and self.trips_polar[i][j + 1][0] > 0.33333:
                    ratios.append(self.accelerations[i][j][1] / self.trips_polar[i][j + 1][0])
            row_features.append(numpy.mean(ratios))

            features.append(row_features)

        numpy.random.shuffle(features)
        num_samples = int(math.floor(sample_size * len(features)))

        train_features = numpy.matrix(features[0:len(features) - num_samples])
        test_features  = numpy.matrix(features[len(features) - num_samples:len(features)])

        norm_train_features = (train_features - numpy.mean(train_features, axis = 0)) / numpy.std(train_features, axis = 0)
        norm_test_features  = (test_features  - numpy.mean(train_features, axis = 0)) / numpy.std(train_features, axis = 0)

        return [norm_train_features, norm_test_features]



def load_drivers(input_path):
    driver_paths = [join(input_path, dirname) for dirname in listdir(input_path) if not isfile(join(input_path, dirname))]
    drivers = [Driver(path) for path in driver_paths]

    return drivers

def produce_global_stats(input_path):
    drivers = load_drivers(input_path)
    all_stats = []

    with open("driver_stats.csv", 'wb') as f:
        tripf = csv.writer(f)
        tripf.writerow(['DriverId', 'MeanDistance', 'MeanTime', 'MaxDistance', 'MedianDistance', 'MinDistance', 'MaxTime', 'MedianTime', 'MinTime'])

        for driver in drivers:
            stats = driver.summary_stats()
            tripf.writerow(stats)
            all_stats.append(stats)
            print stats

    print "loaded all drivers"
    return drivers, stats
