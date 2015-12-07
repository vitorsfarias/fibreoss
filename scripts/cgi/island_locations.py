#!/usr/bin/python

print "Content-type: application/json\n"

from fibreoss import db
import json


database = db.fibreoss()

response=database.fetch_island_locations()
jsonresponse = (json.JSONEncoder().encode(response))
print jsonresponse

