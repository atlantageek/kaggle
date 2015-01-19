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
            driver_ids = self._get_driver_ids()

        for driver_id in driver_ids:
            self.drivers[driver_id] = Driver(driver_id)

    def _get_driver_ids(self):
        c = DB.cursor()
        driver_ids = [r[0] for r in c.execute("SELECT * FROM drivers")]
        c.close()

        return driver_ids

    def features(self, driver_id, sample_size = 0.2):
        driver = self.drivers[driver_id]
        feature_set = driver.current_feature_set()
        return driver.build_features_from_feature_set(feature_set, sample_size)

    def experiment1(self, driver1_id, driver2_id):
        otrain1, otest1, oall1 = self.features(driver1_id)
        otrain2, otest2, oall2 = self.features(driver2_id)

        train1 = otrain1.tolist()
        train2 = otrain2.tolist()
        test1  = otest1.tolist()
        test2  = otest2.tolist()
        training_targets = numpy.array([1] * len(train1) + [-1] * len(train2))
        testing_targets  = numpy.array([1] * len(test1) + [-1] * len(test2))

        train1.extend(train2)
        test1.extend(test2)

        train = numpy.array(train1)
        test = numpy.array(test1)

        clf = svm.SVC(probability = True, kernel = 'rbf', gamma = 0.25)
        clf.fit(train, training_targets)

        results = clf.predict(test)
        probabilities = clf.predict_proba(test)
        self.drivers[driver1_id].clf = clf

        all_results = clf.predict(oall1)
        all_probs   = clf.predict_proba(oall1)

        return [testing_targets, results, probabilities, all_results, all_probs]

    def full_experiment1(self):
        with open("results/experiment1_full_1.csv", 'wb') as f:
            for driver_id in self.drivers.keys():
                driver = self.drivers[driver_id]

                while True:
                    other_driver_id = numpy.random.choice(self.drivers.keys())
                    if other_driver_id != driver_id:
                        break

                exps, preds, probs, all_res, all_probs = self.experiment1(driver_id, other_driver_id)
                for i in xrange(len(all_probs)):
                    f.write("%d_%d,%0.6f\n" % (driver_id, i + 1, all_probs[i][1]))

                acc = 1.0 - numpy.sum(numpy.abs((exps - preds) / 2)) / float(len(exps))
                print "accuracy for driver %d = %0.6f" % (driver_id, acc)
