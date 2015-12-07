# Zenoss-4.x JSON API Connect (python)
#
#Availability report
#needs python 2.7

#------------------------------------------------------------------------------------------------------------------------------
#This script will query the events in zenoss database that fit the date filters
#Returned events will be:
#Events that started before enddate AND ended after startdate
#------------------------------------------------------------------------------------------------------------------------------



import pprint#pretty print


import time
import datetime
import getopt  #getopt argument get
import zenoss_api
import sys

import json

import psql_conn_config as fibreoss_db


DEBUG = 0
HISTORICAL_EVENTS=1



class timedelta(object):
	def __init__(self, start=None, end=None):
		self.start = start
		self.end = end
	def overlap(self, rnglist):
		'''
		@param rnglist is a list of timedeltas to compare the total overlap time
		This functions takes the list and computes the total overlap time of the ranges
		The timedeltas will be sorted by end time and at each iteration the loop subtracts the overlapping intervals
		and sums the overlapping times.
		'''
		tdlist = list(rnglist)
		tdlist.sort(key=lambda t: t.start, reverse=False)
		
		#Performing the union of the events so in the end of the iteration b contains a list of non-overlapping events
		b = []
		for td in tdlist:
				if b and b[-1].end > td.start:
						b[-1].end = max(b[-1].end,td.end)
				else:
						b.append(td)
			
		#B contains the Union of all events in rnglist
		tdlist = list(b)
		tdlist.sort(key=lambda t: t.end, reverse=False)     
		'''
		This next iteration will calculate the intersection of all events in tdlist with the self timerange
		It is assumed that this list contains non-overlapping events, so the list is orderer by the end time of the ranges.
		So, at each iteration the start time of the self timerange is updated to the same value of current iteration end time
		'''
		sum = 0
		
		thisstart = self.start
		for timedelta in tdlist:
			#validate timedelta
			if timedelta.validate()is False:
				continue
			if self.validate() is False:
				return "Invalid Datetime"
			latest_start = max(thisstart, timedelta.start)
			earliest_end = min(self.end, timedelta.end)
			if earliest_end > latest_start:
				sum +=(earliest_end - latest_start).seconds
				thisstart = earliest_end
			else:
				#return "Negative datetime"
				continue
		return datetime.timedelta(seconds=sum)
	def validate(self):
		if self.start <= self.end:
			return True
		else:
			return False
	def show(self):
		return str(self.start) + " " + str(self.end)
	def timerange(self):
		return self.end-self.start

class zendevice(object):
	def __init__(self, name=None, uid=None, productionstate=None):
			self.name = name
			self.uid = uid
			self.productionstate = productionstate
	def show(self):
		return str(self.name) + " " + str(self.uid)

		
		
def get_avail_color(avail):
	if avail == 1.0:
		return "#00FF00"
	elif avail > 0.9:
		return "#FFFF00"
	elif avail > 0.7:
		return "#FF9900"
	else: 
		return "#FF0000"
		
def main(argv):

	#-------------------------------
	#Get command line arguments
	#-------------------------------
	#Default value for enddate is startdate + 24h
	#Default value for outputpath is "/var/www/datasources/zenoss/"
	#DATE INPUT expected in fully ISO-8601 compliant date
	
	SAVE_PATH = "/var/www/datasources/zenoss/"
	parastartdate = ''
	paraenddate = ''
	try:
		opts, args = getopt.getopt(argv,"hs:e:o",["start=","end=","outputpath"])
	except getopt.GetoptError:
		print 'OPTERROR: zenoss_get_avail.py --start <YYYY-mm-ddTHH:MM:SSZ> --end <YYYY-mm-ddTHH:MM:SSZ> --outputpath </var/www/datasources/zenoss/>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'HELP: zenoss_get_avail.py --start <YYYY-mm-ddTHH:MM:SSZ> --end <YYYY-mm-ddTHH:MM:SSZ> --outputpath </var/www/datasources/zenoss/>'
			sys.exit()
		elif opt in ("-s", "--start"):
			parastartdate = arg
		elif opt in ("-e", "--end"):
			paraenddate = arg
		elif opt in ("-o", "--outputpath"):
			SAVE_PATH = arg
		else:
			assert False, "unhandled option"
	#---------------------------------
	print datetime.datetime.now()

	
	
	#---------------------------------
	# Initialize Zenoss API connection
	#---------------------------------
	z = zenoss_api.ZenossAPIExample()
	
	#------
	#date of search
	#datetime.datetime.fromtimestamp(int("1284101485")).strftime('%Y-%m-%d %H:%M:%S')
	#print datetime.datetime.strptime( "2007-03-04 21:08:12", "%Y-%m-%d %H:%M:%S" )
	

   
	
	
	#--------------------------------------------------------------
	# Get devices from Zenoss
	#--------------------------------------------------------------
	rawdevices = z.get_devices()
	
	#if DEBUG:
	#	print json.dumps(rawdevices, indent=4, sort_keys=True)
	
	devices = []
	devcount = rawdevices['totalCount']
	print "Devices: " + str(devcount)
	for dev in rawdevices['devices']:
		# Iterate through each device, and pull the rows we want
		devices.append(zendevice(dev['name'],dev['uid'],dev['productionState']))
	
	if DEBUG:
		for dev in devices:
			print dev.show()
	
	
	
	
	#--------------------------------------------------------------
	#timefilter
	#--------------------------------------------------------------
	#startdt = datetime.datetime(2015,06,01,00,00,00)
	#dayquery = timedelta(startdt,startdt + datetime.timedelta(days=7,seconds=-1))
	#dayquery = timedelta(startdt,datetime.datetime(2015,06,10,23,59,59))
	startdt = datetime.datetime.strptime( parastartdate, "%Y-%m-%dT%H:%M:%SZ" )
	if paraenddate == '':
		enddt = startdt + datetime.timedelta(days=(1))
	else:
		enddt = datetime.datetime.strptime( paraenddate, "%Y-%m-%dT%H:%M:%SZ" )
	dayquery = timedelta(startdt,enddt)
	#---------------------------------------------------------------
	firstday = "2014-01-01 00:00:00" #Date of Zenoss installation
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	filterfirstTime = firstday+'/'+str(dayquery.end.strftime('%Y-%m-%d %H:%M:%S'))
	filterlastTime = str(dayquery.start.strftime('%Y-%m-%d %H:%M:%S'))+'/'+str(now)
	#-------------------------------------------------------------
	
	#--------------------------------------------------------------
	# Get events from Zenoss
	#--------------------------------------------------------------
	#Get current events
	#raw_events = z.get_events(None,None,'/Status/Ping','2014-11-05 00:00:00/2015-06-25 23:59:59')['events']
	
	#raw_events = z.get_current_events(None,None,'/Status/Ping',None)
	#raw_events = z.get_events()
	#Get historical events
	#raw_events = z.get_events_history("virt.uff",None,'/Status/Ping',filterfirstTime,filterlastTime)
	#For test purposes
	#raw_events_current = z.get_current_events(None,None,'/Status/Ping')
	#raw_events_current = z.get_events(None,None,'/Status/Ping')
	
	
	
	#import code
	#code.interact(local=locals())
	
	if HISTORICAL_EVENTS:
		raw_events_archive = z.get_events_history(None,None,'/Status/Ping',filterfirstTime,filterlastTime)
		print "Historical Events: " + str(raw_events_archive['totalCount'])
	
	raw_events_current = z.get_current_events(None,None,'/Status/Ping',filterfirstTime,filterlastTime)
	print "Current Events: " + str(raw_events_current['totalCount'])
	
	#print json.dumps(raw_events, indent=4, sort_keys=True)
	
	#f = open('devices.json','w')
	#f.write(json.dumps(devices, indent=4, sort_keys=True))
	#f.closed
	
	#-------------------------------------------------------------
	#INSERT TO DATABASE
	cur = fibreoss_db.conn.cursor(cursor_factory=fibreoss_db.psycopg2.extras.DictCursor)
	#Init connection
	
	
	
	for dev in devices:

		evtimes = []
		this_ev = None
		
		if HISTORICAL_EVENTS:
			for ev in raw_events_archive['events']:
				if ev['device']['text'] == dev.name:
					# Iterate through raw event data, and pull the rows we want
					start 	= datetime.datetime.strptime( ev['firstTime'], "%Y-%m-%d %H:%M:%S" )
					end 	= datetime.datetime.strptime( ev['lastTime'], "%Y-%m-%d %H:%M:%S" )
					evtimes.append(timedelta(start,end))
					this_ev = ev
				
		for ev in raw_events_current['events']:
			if ev['device']['text'] == dev.name:
				# Iterate through raw event data, and pull the rows we want
				start 	= datetime.datetime.strptime( ev['firstTime'], "%Y-%m-%d %H:%M:%S" )
				end 	= datetime.datetime.strptime( ev['lastTime'], "%Y-%m-%d %H:%M:%S" )
				evtimes.append(timedelta(start,end))
				this_ev = ev		
				

		#import code
		#code.interact(local=locals())		
		
		avail = 1.0-float(dayquery.overlap(evtimes).total_seconds())/float(dayquery.timerange().total_seconds())
		
		if this_ev is None:
			insert_values = "'"+dev.name+"','"+str(dayquery.start)+"','"+str(dayquery.end)+"','no events found','no events found',"+str(avail)+",now()"
		else:
			insert_values = "'"+dev.name+"','"+str(dayquery.start)+"','"+str(dayquery.end)+"','"+str(this_ev['eventClass']['uid'])+"','"+str(this_ev['summary'])+"',"+str(avail)+",now()"
		
		if DEBUG:
			print dev.show() + " " + str(avail)
			for ev in evtimes:
				print ev.show()
		
		#-------------------------------------------------------------
		#INSERT TO DATABASE
		
		try:
			cur.execute("INSERT INTO zenoss_avail("
			"device_text,timedelta_start,timedelta_end,event_class_uid,summary,availability,entry_time"
			") VALUES("
			+insert_values+
			");")
			fibreoss_db.conn.commit()
			
		except fibreoss_db.psycopg2.DatabaseError, e:
			
			if fibreoss_db.conn:
				fibreoss_db.conn.rollback()
			
			print 'Error %s' % e    
			sys.exit(1)
			
		
		#output results into an html file to be displayed in the LS_WEB
		#Each query generates a table with a single column 
		avail_in_percent = "{:10.2f}".format(avail*100)
		bgcolor = get_avail_color(avail)


	

	
	#close connection		
	#if fibreoss_db.conn:
	#	fibreoss_db.conn.close()

	
	#---------------------------------------------------
	#Generate week report quering from the fibreoss db
	#---------------------------------------------------
	
	DAYS = 7 # A week
	
	weekquery = timedelta(startdt + datetime.timedelta(days=-(DAYS-1)),enddt)

	
	
	
	#Prepare the html file
	html = (
	"<table id='availability' class='display' cellspacing='0' width='100%' border='1'>\n"
	"<thead>\n"
	"<tr><th>Device_Text</th><th>Prod. State</th>"
	)
	for i in range(DAYS):
		curdate = weekquery.start + datetime.timedelta(days=i+1)
		html += "<th>"+str(curdate.strftime('%B-%d'))+"</th>"
	
	html += (
	"</tr>\n"
	"</thead>\n"
	"<tbody>\n"
	)
	
	
	#Para cada dispositivo, consulta todos os eventos da semana
	
	for dev in devices:
		
		html += "<tr>"
		html += "<td>"+str(dev.name)+"</td>"
		if dev.productionstate == 1000:
			html += "<td>Production</td>"
		elif dev.productionstate == 300:
			html += "<td>Maintenance</td>"
		else:
			html += "<td>"+str(dev.productionstate)+"</td>"
		
		cur = fibreoss_db.conn.cursor(cursor_factory=fibreoss_db.psycopg2.extras.DictCursor)
		#query = "SELECT * FROM zenoss_avail WHERE device_text='"+str(dev.name)+"' AND timedelta_start >='"+weekquery.start.strftime('%Y-%m-%d %H:%M:%S')+"'::timestamp AND timedelta_end <='"+weekquery.end.strftime('%Y-%m-%d %H:%M:%S')+"'::timestamp ORDER by entry_time DESC;"
		#query = "SELECT * FROM zenoss_avail WHERE device_text='"+str(dev.name)+"' AND timedelta_start >='"+weekquery.start.strftime('%Y-%m-%d %H:%M:%S')+"'::timestamp AND timedelta_end <='"+weekquery.end.strftime('%Y-%m-%d %H:%M:%S')+"'::timestamp ORDER by timedelta_start ASC,entry_time DESC;"
		query = "SELECT DISTINCT ON (timedelta_start) timedelta_start,device_text,availability,entry_time FROM zenoss_avail WHERE device_text='"+str(dev.name)+"' AND timedelta_start >='"+weekquery.start.strftime('%Y-%m-%d %H:%M:%S')+"'::timestamp AND timedelta_end <='"+weekquery.end.strftime('%Y-%m-%d %H:%M:%S')+"'::timestamp ORDER by timedelta_start ASC,entry_time DESC;"
		#print query
		
		try:
			cur.execute(query)
		except:
			print "Database error"

		#
		# Note that below we are accessing the row via the column name.
		result = cur.fetchall()
		

		
		#for row in rows:
		#	print "   ", row['device_text']
		
		#pprint.pprint(result)
		for i in range(DAYS):
			avail_in_percent = ''
			bgcolor=''
			curdate = weekquery.start + datetime.timedelta(days=i)			
			
			
			for row in result:
				evdate = row['timedelta_start']
				if curdate == evdate:
					avail_in_percent = "{:10.2f}".format(row['availability']*100)
					bgcolor = get_avail_color(row['availability'])
					
			html += "<td bgcolor='"+bgcolor+"'>"+str(avail_in_percent)+"</td>"
			
		html += "</tr>\n"
	
	
	#close connection		
	if fibreoss_db.conn:
		fibreoss_db.conn.close()
	
	
	html += (
	"</tbody>\n"
	"</table>\n"
	)
	date = dayquery.start.strftime('%Y-%m-%d')
	f = open(SAVE_PATH+'zenoss_week_avail_'+date+'.html','w')
	f.write(html)
	#f.closed
	f.close()
	
	
if __name__ == "__main__":
	main(sys.argv[1:])

