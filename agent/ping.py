# Zenoss-4.x JSON API Connect (python)
#
#Ping devices
#needs python 2.7

#------------------------------------------------------------------------------------------------------------------------------
#Receives a list of devices and starts threads to ping them
#------------------------------------------------------------------------------------------------------------------------------

from fibreoss import common
import fibreoss

import pprint#pretty print

import time
import datetime
import getopt  #getopt argument get
import sys,os

import json

import os
import platform
import subprocess
import Queue
import threading




DEBUG = 1
ENABLE_PSQL = 1

#CONNECT TO POSTGRE DB
#fibreoss_db = fibreoss.config.PG_CONNECT
#AGENT_NAME = os.path.dirname(os.path.realpath(__file__)) + "/" + __file__ 
AGENT_NAME = __file__





'''
class zendevice(object):
	def __init__(self, name=None, uid=None, productionstate=None,ipstring=None):
			self.name = name
			self.uid = uid
			self.productionstate = productionstate
			self.ipstring = ipstring
	def show(self):
		return str(self.name) + " " + str(self.uid) + " " + str(self.ipstring)
'''		
		
'''
def insert_PING_TESTS_table(insert_values):
	
	#-------------------------------------------------------------
	#INSERT TO DATABASE

	try:
		cur.execute("INSERT INTO ping_tests("
		"test_name,test_parameters,test_subject,test_results,test_time,agent,test_subject_url,return_code,test_id"
		") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",insert_values)
		fibreoss.config.PG_CONNECT.commit()
		
	except fibreoss.config.psycopg2.DatabaseError, e:
		
		if fibreoss.config.PG_CONNECT:
			fibreoss.config.PG_CONNECT.rollback()
		
		print 'Error %s' % e	
		sys.exit(1)
		
#--------------------------------------------------------
'''
def worker_func(ping_args, pending, done):
	try:
		while True:
		
		
			# Get the next address to ping.
			device = pending.get_nowait()
			address = device.ipstring

			ping = subprocess.Popen(ping_args + [address],
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE
			)
			out, error = ping.communicate()
			returncode = ping.returncode
			
			result={'device':device,'returncode':returncode,'out':out,'error':error}
			
			# Output the result to the 'done' queue.
			done.put(result)
	except Queue.Empty:
		# No more addresses.
		pass
	finally:
		# Tell the main thread that a worker is about to terminate.
		done.put(None)
		
def ping(devices):


	database = fibreoss.db.fibreoss()


	#must become a log entry
	print "#----------------------------------------"
	print datetime.datetime.now()
	print AGENT_NAME
	print 'Total devices: ' + str(len(devices))
	print "#----------------------------------------"
	
	#import code
	#code.interact(local=locals())	

	'''
	#--------------------------------------------------------------
	#INSTANTIATE ZENOSS API
	#--------------------------------------------------------------
	zenoss = fibreoss.api.zenoss.jsonapi()

	#--------------------------------------------------------------
	# Get devices from Zenoss
	#--------------------------------------------------------------
	rawdevices = zenoss.get_devices()
	
	
	#if DEBUG:
	#	print json.dumps(rawdevices, indent=4, sort_keys=True)
	
	devices = []
	devcount = rawdevices['totalCount']
	print "Devices: " + str(devcount)
	for dev in rawdevices['devices']:
		# Iterate through each device, and pull the rows we want
		devices.append(fibreoss.api.zenoss.zendevice(dev['name'],dev['uid'],dev['productionState'],dev['ipAddressString']))
	
	#if DEBUG:
	#	for dev in devices:
	#		print dev.show()
	
	#-------------------------------------------
	#PING TEST
	#-----------------------------------------	
	
	# The number of workers.
	NUM_WORKERS = 10
	'''

	plat = platform.system()
	#scriptDir = sys.path[0]
	#hosts = os.path.join(scriptDir, 'hosts.txt')
	

	# The arguments for the 'ping', excluding the address.
	if plat == "Windows":
		pingArgs = ["ping", "-n", "1", "-l", "1", "-w", "100"]
	elif plat == "Linux":
		pingArgs = ["ping", "-c", "1", "-l", "1", "-s", "1", "-W", "1"]
	else:
		raise ValueError("Unknown platform")

	# The queue of addresses to ping.
	pending = Queue.Queue()

	# The queue of results.
	done = Queue.Queue()

	# Create all the workers.
	workers = []
	for _ in range(fibreoss.config.NUM_WORKERS):
		workers.append(threading.Thread(target=worker_func, args=(pingArgs, pending, done)))

	
	# Put all the addresses into the 'pending' queue.
	for dev in devices:
		#print dev.show()
		
		pending.put(dev)
		
	# Start all the workers.
	for w in workers:
		w.daemon = True
		w.start()

	# Print out the results as they arrive.
	numTerminated = 0
	
	
	while numTerminated < fibreoss.config.NUM_WORKERS:
		result = done.get()
		if result is None:
			# A worker is about to terminate.
			numTerminated += 1
		else:
			device = result['device']
			device_name = device.name
			device_uri = device.uri
			control_ip = device.ipstring
			returncode = result['returncode']
			ping_response = result['out']
			#print result
			
			
			test_subject_uri = 'control'+'.'+'network'+'.'+device_uri
			if returncode == 0:
			#Ping OK
				print str(device_uri) + ' ' + str(control_ip) + ' is UP'
				insert_values = ("DEVICE_PING_TEST",ping_response,device_name,control_ip + ' is UP','now()',AGENT_NAME,test_subject_uri,0,40001)
			elif returncode == 1:
			#ping NOK
				print str(device_name) + ' ' + str(control_ip) + ' is DOWN'
				insert_values = ("DEVICE_PING_TEST",ping_response,device_name,control_ip + ' is DOWN','now()',AGENT_NAME,test_subject_uri,1,40001)
			if ENABLE_PSQL: 
				database.insert_ping_test(insert_values)

			#print insert_values
			

	# Wait for all the workers to terminate.
	for w in workers:
		w.join()
	
'''
#close DB connection		
if fibreoss.db.conn:
	fibreoss.db.conn.close()  
'''	
