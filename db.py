from os import listdir
from os.path import isfile, join

import sys
import sqlite3
import string
from driver import Driver

DB_PATH = "data/drivers.db"
DB = sqlite3.connect(DB_PATH)

def create_trips_table():
    c = DB.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trips
                    (
                        driver_id INTEGER, trip_id INTEGER, t INTEGER, x REAL, y REAL,
                        r REAL, theta REAL, alpha REAL, omega REAL,
                        PRIMARY KEY (driver_id, trip_id, t)
                    ) WITHOUT ROWID''')

    DB.commit()

def create_trips_table_indexes():
    c = DB.cursor()
    c.execute('''CREATE INDEX IF NOT EXISTS trips_driver_r ON trips
                    (
                        driver_id, r
                    )''')
    c.execute('''CREATE INDEX IF NOT EXISTS trips_driver_theta ON trips
                    (
                        driver_id, theta
                    )''')
    c.execute('''CREATE INDEX IF NOT EXISTS trips_driver_alpha ON trips
                    (
                        driver_id, alpha
                    )''')
    c.execute('''CREATE INDEX IF NOT EXISTS trips_driver_r_omega ON trips
                    (
                        driver_id, r, omega
                    )''')
    DB.commit()

def create_drivers_table(data_path):
    c = DB.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS drivers
                    (
                        id INTEGER,
                        PRIMARY KEY (id)
                    ) WITHOUT ROWID''')

    driver_ids = sorted([int(dirname) for dirname in listdir(data_path) if not isfile(join(data_path, dirname))])

    for driver_id in driver_ids:
        c.execute("INSERT INTO drivers (id) VALUES (%d)" % (driver_id))

    DB.commit()



def populate_trips_table(data_path):
    create_trips_table()
    c = DB.cursor()

    driver_ids = sorted([int(dirname) for dirname in listdir(data_path) if not isfile(join(data_path, dirname))])
    driver_paths = [join(data_path, str(driver_id)) for driver_id in driver_ids]

    for driver in (Driver(path) for path in driver_paths):
        driver.compute_accelerations()
        for i in xrange(len(driver.trips)):
            for j in xrange(len(driver.trips[i])):
                if j == 0:
                    accels = [0.0, 0.0]
                else:
                    accels = [driver.accelerations[i][j - 1][0], driver.accelerations[i][j - 1][1]]
                params = (
                    driver.driver_id, i + 1, j, driver.trips[i][j][0], driver.trips[i][j][1],
                    driver.trips_polar[i][j][0], driver.trips_polar[i][j][1],
                    accels[0], accels[1]
                )
                c.execute(
                    "INSERT INTO trips (driver_id, trip_id, t, x, y, r, theta, alpha, omega)"
                    "VALUES (%d, %d, %d, %0.4f, %0.4f, %0.6f, %0.6f, %0.6f, %0.6f)" % params
                )
            DB.commit()


# data_path = sys.argv[1]

# print "Creating drivers table with data directory = %s..." % (data_path)
# create_drivers_table(data_path)

# print "Creating trips table..."
# create_trips_table()

# print "Populating trips table with data directory = %s" % (data_path)
# populate_trips_table(data_path)
