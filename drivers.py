import sqlite3
import numpy
import math

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

    def format_features_for_output(self, driver_id):
        return None
