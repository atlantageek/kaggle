import sqlite3
import string
import numpy
import math

from sklearn import svm
from driver import Driver

DB_PATH = "data/drivers.db"
DB = sqlite3.connect(DB_PATH)

class Drivers(object):
    def __init__(self, driver_ids = None):
        self.drivers = {}

        if driver_ids is None:
            self.driver_ids = self._get_driver_ids()
        else:
            self.driver_ids = driver_ids[:]

        for driver_id in self.driver_ids:
            self.drivers[driver_id] = {}

    def _get_driver_ids(self):
        c = DB.cursor()
        driver_ids = [r[0] for r in c.execute("SELECT * FROM drivers")]
        c.close()

        return driver_ids

    def features(self, driver_id):
        num_trips = self.trip_count(driver_id)
        trips = self.get_trip_stats(driver_id)

        if len(trips) != num_trips:
            raise Exception("Length of trips does not match count from the database.")

        return trips

    def random_opposing_features(self, driver_id):
        num_trips = self.trip_count(driver_id)
        opp_trips = self.get_opposing_trip_stats(driver_id)

        if len(opp_trips) != num_trips:
            raise Exception("Length of opposing trips does not match count from the database.")

        return opp_trips

    def get_trip_stats(self, driver_id):
        if self.drivers[driver_id].has_key('trips'):
            return self.drivers[driver_id]['trips']

        c = DB.cursor()
        trips = []

        for trip in c.execute("SELECT * FROM feature_set1 WHERE driver_id = %d ORDER BY trip_id ASC" % (driver_id)):
            trips.append(trip[2:])

        self.drivers[driver_id]['trips'] = numpy.array(trips)
        return self.drivers[driver_id]['trips']

    def get_opposing_trip_stats(self, driver_id):
        if self.drivers[driver_id].has_key('opp_trips'):
            return self.drivers[driver_id]['opp_trips']

        num_to_oppose = self.trip_count(driver_id)
        opposing_driver_id = self.choose_random_opposing_driver_id(driver_id)

        c = DB.cursor()
        qry = """SELECT * FROM feature_set1
                 WHERE driver_id = %d
                 ORDER BY trip_id ASC LIMIT %d""" % (opposing_driver_id, num_to_oppose)

        opp_trips = []
        for trip in c.execute(qry):
            opp_trips.append(trip[2:])

        self.drivers[driver_id]['opp_trips'] = numpy.array(opp_trips)
        return self.drivers[driver_id]['opp_trips']

    def choose_random_opposing_driver_id(self, driver_id):
        while True:
            opp_id = numpy.random.choice(self.driver_ids, size = 1, replace = False)
            if opp_id != driver_id:
                break
        return opp_id

    def trip_count(self, driver_id):
        if self.drivers[driver_id].has_key('trip_count'):
            return self.drivers[driver_id]['trip_count']

        c = DB.cursor()
        c.execute("SELECT COUNT(*) AS trip_count FROM feature_set1 WHERE driver_id = %d" % (driver_id))
        r = c.fetchone()

        self.drivers[driver_id]['trip_count'] = r[0]
        return r[0]


    def experiment1(self, driver_id, sample_size = 0.2):
        base_pos = self.features(driver_id)
        base_neg = self.random_opposing_features(driver_id)

        base_pos_indexes = range(len(base_pos))
        base_neg_indexes  = range(len(base_neg))

        num_samples = math.floor(len(base_pos_indexes) * 0.2)
        test_pos_idxs  = sorted(numpy.random.choice(base_pos_indexes, size = num_samples, replace = False))
        train_pos_idxs = [i for i in base_pos_indexes if i not in test_pos_idxs]

        test_neg_idxs  = sorted(numpy.random.choice(base_neg_indexes, size = num_samples, replace = False))
        train_neg_idxs = [i for i in base_neg_indexes if i not in test_neg_idxs]

        train = [base_pos[i] for i in train_pos_idxs] + [base_neg[i] for i in train_neg_idxs]
        test  = [base_pos[i] for i in test_pos_idxs]  + [base_neg[i] for i in test_neg_idxs]

        training_targets = numpy.array([1] * len(train_pos_idxs) + [-1] * len(train_neg_idxs))
        testing_targets  = numpy.array([1] * len(test_pos_idxs) + [-1] * len(test_neg_idxs))

        clf = svm.SVC(probability = True, kernel = 'rbf', gamma = 0.25)
        clf.fit(train, training_targets)

        results = clf.predict(test)
        probabilities = clf.predict_proba(test)

        base = numpy.array(base_pos.tolist() + base_neg.tolist())
        base_targets = numpy.array([1] * len(base_pos) + [-1] * len(base_neg))

        clf = svm.SVC(probability = True, kernel = 'rbf', gamma = 0.25)
        clf.fit(base, base_targets)

        all_results = clf.predict(base_pos)
        all_probs   = clf.predict_proba(base_pos)

        return [testing_targets, results, probabilities, all_results, all_probs]

    def full_experiment1(self, run_id = 1):
        with open("results/experiment1_full_%d.csv" % (run_id), 'wb') as f:
            for driver_id in self.driver_ids:
                exps, preds, probs, all_res, all_probs = self.experiment1(driver_id)

                for i in xrange(len(all_probs)):
                    f.write("%d_%d,%0.6f\n" % (driver_id, i + 1, all_probs[i][1]))

                acc = 1.0 - numpy.sum(numpy.abs((exps - preds) / 2)) / float(len(exps))
                print "accuracy for driver %d = %0.6f" % (driver_id, acc)
