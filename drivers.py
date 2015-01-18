import sqlite3
import string
import numpy
import math
import svmlight

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

    def format_features_for_output(self, driver_id, sample_size = 0.2):
        driver = self.drivers[driver_id]
        feature_set = driver.current_feature_set()
        train, test = driver.build_features_from_feature_set(feature_set, sample_size)

        output_train = []
        output_test  = []

        def _format_row(ftrs):
            return string.join(["%d:%0.6f" % (i + 1, ftrs[0, i]) for i in xrange(ftrs.shape[1])], ' ')

        for i in xrange(len(train)):
            row = train[i]
            ftr_str = _format_row(row)
            output_train.append(ftr_str)
        for i in xrange(len(test)):
            row = test[i]
            ftr_str = _format_row(row)
            output_test.append(ftr_str)

        return [output_train, output_test]

    def experiment1(self, path_and_prefix, driver1_id, driver2_id):
        otrain1, otest1 = self.format_features_for_output(driver1_id)
        otrain2, otest2 = self.format_features_for_output(driver2_id)

        train_filename = "%s-train.dat" % (path_and_prefix)
        test_filename  = "%s-test.dat" % (path_and_prefix)

        expected_results = numpy.concatenate([numpy.ones(len(otest1)), numpy.zeros(len(otest2))])

        with open(train_filename, 'wb') as trainf:
            for line in otrain1:
                trainf.write("1 %s\n" % (line))
            for line in otrain2:
                trainf.write("-1 %s\n" % (line))

        with open(test_filename, 'wb') as testf:
            for line in otest1:
                testf.write("1 %s\n" % (line))
            for line in otest2:
                testf.write("-1 %s\n" % (line))

        svm = svmlight.SVMLight(path_and_prefix)
        results = svm.run()

        print expected_results
        print results

        return self.pav(expected_results, results)

    def pav(self, expected, results):
        data = sorted(zip(expected, results, expected), key = lambda x: x[1])

        output = []
        grp = []

        for i in xrange(0, len(data) - 1):
            if data[i][0] > data[i + 1][0]:
                if len(grp) > 0:
                    avg = sum([x[0] for x in grp]) / float(len(grp))
                    for g in grp:
                        output.append((avg, g[1], g[2]))
                grp = [data[i]]
            else:
                grp.append(data[i])

        if len(grp) > 0:
            avg = sum([x[0] for x in grp]) / float(len(grp))
            for g in grp:
                output.append((avg, g[1], g[2]))

        return output
