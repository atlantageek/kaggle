#!/usr/bin/python

import sqlite3 as lite
from sklearn import svm
import sys

con = None

try:
    con = lite.connect('data/drivers.db')
    cur = con.cursor()
    cur.execute('update trip_stats set rval=random()')
    cur.execute('SELECT * from trip_stats where driver_id != 1 order by rval limit 200')
    data = cur.fetchall()
    training_data = []
    expected_data = []
    for row in data:
        new_row = row[2:9]
        training_data.append(new_row)
        expected_data.append(0)

    cur.execute('SELECT * from trip_stats where driver_id = 1 limit 200')
    data = cur.fetchall()
    for row in data:
        new_row = row[2:9]
        training_data.append(new_row)
        expected_data.append(1)

    print "Dataset Built"
    cur.execute('update trip_stats set rval=random()')
    cur.execute('select * from trip_stats where driver_id=1 or driver_id = 2 order by rval')
    data = cur.fetchall()
    clf = svm.SVC(probability=True)
    clf.fit(training_data, expected_data)
    print "Model built"
    for row in data:
        target_data = row[2:9]
        print row[0], clf.predict(target_data)[0], clf.predict_proba(target_data)[0]

except lite.Error, e:
    print "Error %s:" % e.args[0]
    sys.exit(1)

finally: 
    if con: 
        con.close()
