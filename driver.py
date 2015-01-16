import sqlite3
import numpy
import math

DB_PATH = "data/drivers.db"
DB = sqlite3.connect(DB_PATH)

class Driver(object):
    def __init__(self, driver_id):
        self.driver_id = int(driver_id)

    # NOTE: rename this method and create a new one whenever you change the feature set
    def current_feature_set(self):
        """
        all features computed for values where the velocity is in the interval [4,40] m/s

        MAX(ABS(omega)) - highest angular velocity
        MAX(alpha) - fastest acceleration
        MIN(alpha) - fastest deceleration
        AVG(r) - mean velocity
        MAX(r) - highest velocity
        MAX(omega / r) - the most Gs in a turn
        """
        results = []
        q1 = """SELECT MAX(ABS(omega)), MAX(alpha), MIN(ALPHA), AVG(r), MAX(r), MAX(omega / r)
                FROM trips WHERE driver_id = %d AND r BETWEEN 4 AND 40
                GROUP BY driver_id, trip_id""" % (self.driver_id)
        c = DB.cursor()
        for trip in c.execute(q1):
            results.append(trip)

        return numpy.matrix(results)

    def build_features_from_feature_set(self, feature_set, sample_size = 0.2):
        numpy.random.shuffle(feature_set)
        num_samples = int(math.floor(sample_size * len(feature_set)))

        train_features = numpy.matrix(feature_set[0:len(feature_set) - num_samples])
        test_features  = numpy.matrix(feature_set[len(feature_set) - num_samples:len(feature_set)])

        norm_train_features = (train_features - numpy.mean(train_features, axis = 0)) / numpy.std(train_features, axis = 0)
        norm_test_features  = (test_features  - numpy.mean(train_features, axis = 0)) / numpy.std(train_features, axis = 0)

        return [norm_train_features, norm_test_features]
