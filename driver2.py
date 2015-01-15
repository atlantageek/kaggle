import sqlite3

DB_PATH = "data/drivers.db"
DB = sqlite3.connect(DB_PATH)

class Driver2(object):
    def __initialize__(self, driver_id):
