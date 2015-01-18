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
        otrain1, otest1 = self.features(driver1_id)
        otrain2, otest2 = self.features(driver2_id)

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

        return [testing_targets, results, probabilities, clf]
