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

class Driver:
    def __init__(self, path):
        self.path = path
        self.files = [fname for fname in listdir(path) if isfile(join(path, fname))]
        self.trips = []
        self._load_trips()

    def _load_trips(self):
        for fname in self.files:
            with open(join(self.path, fname), 'rb') as f:
                tripf = csv.reader(f)
                tripf.next()  # header row
                coords = [(float(row[0]), float(row[1])) for row in tripf]

                print "Loaded %s with %d rows" % (join(self.path, fname), len(coords))
                self.trips.append(numpy.array(coords))

# input_path = sys.argv[1]
# driver_paths = [dirname for dirname in listdir(input_path) if not isfile(join(input_path, dirname))]

driver_path = sys.argv[1]

driver = Driver(driver_path)

print driver.trips[0]
