import sqlite3
import numpy
import math

DB_PATH = "data/drivers.db"
DB = sqlite3.connect(DB_PATH)

class Driver(object):
    def __init__(self, driver_id):
        self.driver_id = int(driver_id)
        self.clf = None

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
        q1 = """SELECT trip_id, MAX(ABS(omega)), MAX(alpha), MIN(alpha), AVG(r), MAX(r), MAX(omega / r)
                FROM trips WHERE driver_id = %d AND r >= 4.0 AND r <= 40.0
                GROUP BY trip_id

                UNION

                SELECT trip_id, 3.14159, MAX(alpha), MIN(alpha), AVG(r), 4.0, 1.0
                FROM trips WHERE driver_id = %d
                GROUP BY trip_id HAVING MAX(r) < 4.0

                UNION

                SELECT trip_id, 3.14159, 10.0, -10.0, AVG(r), 40.0, 10.0
                FROM trips WHERE driver_id = %d
                GROUP BY trip_id HAVING MIN(r) > 40.0

                ORDER BY trip_id ASC
        """ % (self.driver_id, self.driver_id, self.driver_id)
        c = DB.cursor()
        for trip in c.execute(q1):
            results.append(trip)

        return numpy.matrix(results)

    def build_features_from_feature_set(self, feature_set, sample_size = 0.2):
        numpy.random.shuffle(feature_set)
        num_samples = int(math.floor(sample_size * len(feature_set)))

        train_features = numpy.matrix(feature_set[0:len(feature_set) - num_samples])
        test_features  = numpy.matrix(feature_set[len(feature_set) - num_samples:len(feature_set)])
        all_features   = numpy.matrix(feature_set[:])

        norm_train_features = (train_features - numpy.mean(train_features, axis = 0)) / numpy.std(train_features, axis = 0)
        norm_test_features  = (test_features  - numpy.mean(train_features, axis = 0)) / numpy.std(train_features, axis = 0)
        norm_all_features   = (all_features   - numpy.mean(train_features, axis = 0)) / numpy.std(train_features, axis = 0) # abbey norm all

        return [norm_train_features, norm_test_features, norm_all_features]
