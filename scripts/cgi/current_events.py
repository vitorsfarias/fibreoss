#!/usr/bin/python

#print "Content-type: text/html"
print "Content-type: application/json"
print

from fibreoss import db
import json
import datetime
import cgitb

#change when passing into production
#cgitb.enable()
cgitb.enable(display=0, logdir="/var/log/fibreoss/")



database = db.fibreoss()

response=database.fetch_current_events()

stringresponse = []
for row in response:
	stringrow = {}
	for key,value in row.items():
		if key in ['id','test_id']:
			stringrow[key] = str(value)
		elif key == 'test_time':
			stringrow[key] = value.strftime("%Y-%m-%d %H:%M:%S")
		elif key in ['event_level','test_subject_url','return']:
			stringrow[key] = value
	
	stringresponse.append(stringrow)

jsonresponse = (json.JSONEncoder().encode(stringresponse))
print jsonresponse

