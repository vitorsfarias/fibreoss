

import fibreoss


from __future__ import division

import sys, getopt

import psql_conn_config as fibreoss_db

import datetime
import re

DEBUG = 0



def print_tree(node,level=0):
        for i in range(level):
                print "\t",
        print node.label
        for device in node.devices:
                for i in range(level):
                        print "\t",
                print "- <"+device.name+"("+str(device.availability)+")"+">"
        for child in node.children:
                print_tree(child,level+1)


def get_avail_color(avail):
	for limit in fibreoss.config.AVAILABILITY_COLOR_CODE:
		if avail >= float(limit['min']):

			return(limit['color'])				


class availability_report(object):
	"""
	Generates an availability report for the federation islands
	Receives as input a list of device objects
	
	"""

	def __init__(self, date):
		self.date = date
		self.island_devices = {}
		self.island_nodes = {}
		#self.result = {}
	
		
	def init_islands_dictionaries(self,result):	
		#Creates a dictionary of device object list. Each island has a key.
		#island_devices = {}
		#island_nodes = {}
		for row in result:
			device_text = row['device_text']
			device_text = device_text.split('.')
			try:
				#At this point i had to assume that all names will have the structure: device.island.fibre.org.br And will catch the -4 element
				island = device_text[-4]
			except:
				continue		
			
			self.island_devices[island] = []
			self.island_nodes[island] = {}	
	def init_devices_dictionaries(self,result):
		'''
		Parses devices from queries and append to device list
		'''
		for row in result:
			#evdate = row['timedelta_start']
			#if date == evdate:
			#	avail_in_percent = "{:10.2f}".format(row['availability']*100)
			#	bgcolor = get_avail_color(row['availability'])
			device_text = row['device_text']
			availability = row['availability']
			
			device_text = device_text.split('.')
			try:
				#island = device_text[1]
				island = device_text[-4]
			except:
				continue
			#device_name = device_text[0]		
			
			#creates device object in island list
			self.island_devices[island].append(device(row['device_text'],availability))
			
			if DEBUG:
				print island + " " + row['device_text']
				
	def init_nodes_dictionaries(self):
		#Creates nodes dictionary		
		for island in self.island_devices:
			
			#Create node Accesories:
			if 'accessories' not in self.island_nodes[island]:
				self.island_nodes[island]['accessories'] = node('accessories',[])
			
			for device in self.island_devices[island]:
				#Declare nodes	

				node_name = device.affiliation()
				if node_name is None:
					continue
				
				if DEBUG:
					print device.name + " " + node_name
						
				#If the node does not exists, create node
				if node_name not in self.island_nodes[island]:
					self.island_nodes[island][node_name] = node(node_name,[])
				
				#Some nodes will have multiple instances (netfpga and icarus)	
				
				#Append device to its node
				self.island_nodes[island][node_name].devices.append(device)


		#Assigns relationships
		for island in self.island_nodes.keys():
			for node_name in self.island_nodes[island].keys():
				
				if DEBUG:
					print str(island) + " " + str(node_name)
				#parse dict through all nodes
				this_node = self.island_nodes[island][node_name]
				for child in this_node.affiliation('children'):
					
					
					#check if the node exists within the island and add it as child
					#if child in island_nodes[island].keys():
					for key in self.island_nodes[island].keys():
						m = re.match(child, key)
						if m is not None:
							child_node = self.island_nodes[island][key]
							this_node.add_child(child_node)


#------------------------------------------------------------------	
host='all'
#default is yesterday
date=datetime.datetime.now() + datetime.timedelta(days=(-1))
SAVE_PATH = "/var/www/datasources/islands_avail/"

#------------------------------------------------------------------

# Read command line args
myopts, args = getopt.getopt(sys.argv[1:],"H:d:")
 
###############################
# o == option
# a == argument passed to the o
###############################
for o, a in myopts:
	if o == '-H':
		host=a
	elif o == '-d':
        #date = datetime.datetime.strptime( a, "%Y-%m-%dT%H:%M:%SZ" )
		date = datetime.datetime.strptime( a, "%Y-%m-%d" )
	elif o == '-o':
		SAVE_PATH=a
	else:
		print("Usage: %s -d <YYYY-mm-dd>" % sys.argv[0])
 #example
 #python availability_calc.py - portal.uff.fibre.org.br -u <user> -p <pwd> [-n node1,node2,node3] 



							
#daily_report = availability_report(datetime.datetime.strptime( '2015-10-18', "%Y-%m-%d" ))
#result = daily_report.fetch_zenoss()
#daily_report.init_islands_dictionaries(result)
#daily_report.init_devices_dictionaries(result)
#daily_report.init_nodes_dictionaries()

						
							
#import code
#code.interact(local=locals())	
'''							
#Prints the island tree
for island in island_nodes.keys():
	print '--------------------------------------------------------'
	print island
	print '--------------------------------------------------------'
	if 'infrastructure' in island_nodes[island].keys():
		root = island_nodes[island]['infrastructure']
		print "Infrastructure AVAIL: " + str(root.node_avail())
		print_tree(root)
	if 'accessories' in island_nodes[island].keys():
		accessories = island_nodes[island]['accessories']
		print "Accessories AVAIL: " + str(accessories.node_avail())
		print_tree(accessories)
'''	


#Gera dict para report em html
DAYS = 7 # A week
startdate = date - datetime.timedelta(days=DAYS)
WEEK_REPORT = {}

#generate table with week results
for i in range(DAYS):
	curdate = startdate + datetime.timedelta(days=i+1)
	
	str_curdate = curdate.strftime('%Y-%m-%d')
	
	daily_report = availability_report(curdate)
	result = daily_report.fetch_zenoss()
	daily_report.init_islands_dictionaries(result)
	daily_report.init_devices_dictionaries(result)
	daily_report.init_nodes_dictionaries()

	if str_curdate not in WEEK_REPORT.keys():
		WEEK_REPORT[str_curdate] = {}


	for island in daily_report.island_nodes.keys():
		#print '--------------------------------------------------------'
		#print island
		#print '--------------------------------------------------------'
		if 'infrastructure' in daily_report.island_nodes[island].keys():
			root = daily_report.island_nodes[island]['infrastructure']
			#print "Infrastructure AVAIL: " + str(root.node_avail())
			if island not in WEEK_REPORT[str_curdate].keys():
				WEEK_REPORT[str_curdate][island] = {}
			
			WEEK_REPORT[str_curdate][island] = root.node_avail()

		
#-------------------------------------------------------------------------------------

#Prepare the html file
html = (
"<table id='availability' class='display' cellspacing='0' width='100%' border='1'>\n"
"<thead>\n"
"<tr><th>Island</th><th>Description</th>"
)
for i in range(DAYS):
	curdate = startdate + datetime.timedelta(days=i+1)
	html += "<th>"+str(curdate.strftime('%B-%d'))+"</th>"

html += (
"</tr>\n"
"</thead>\n"
"<tbody>\n"
)
#---------BODY
str_curdate = (startdate + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
for island in WEEK_REPORT[str_curdate].keys():
	
	html += (
	"<tr>"
	"<td>"+island+"</td><td>-</td>\n"
	)
	for i in range(DAYS):	
		curdate = startdate + datetime.timedelta(days=i+1)
		str_curdate = curdate.strftime('%Y-%m-%d')
		if island in WEEK_REPORT[str_curdate].keys():
			availability = WEEK_REPORT[str_curdate][island]
			avail_in_percent = "{:10.2f}".format(availability*100)
			bgcolor = get_avail_color(availability)
		
			html += "<td bgcolor='"+bgcolor+"'>"+str(avail_in_percent)+"</td>"
		else:
			html += "<td>-</td>"
	html += (
	"</tr>\n"
	)
		
	


html += (
"</tbody>\n"
"</table>\n"
)
#date = dayquery.start.strftime('%Y-%m-%d')

str_date=date.strftime('%Y-%m-%d')	
f = open(SAVE_PATH+'islands_week_avail_'+str_date+'.html','w')
f.write(html)
f.close()


				
#import code
#code.interact(local=locals())		

			

#close connection		
if fibreoss_db.conn:
	fibreoss_db.conn.close()



'''	
#Declare devices
#Declare nodes	
#------------------------	
virt = device("virt",0.99)
tor = device("tor",0.98)
ldap = device("ldap",0.97)
vpn = device("vpn",0.96)
#------------------------
ocf = device("ocf",0.95)
flowvisor = device("flowvisor",0.94)
pronto = device("pronto",0.93)
netfpga1 = device("netfpga1",0.92)
netfpga2 = device("netfpga2",0.91)
netfpga3 = device("netfpga3",0.90)
#------------------------
omf = device("omf",0.89)
icarus1 = device("icarus1",0.78)
icarus2 = device("icarus2",0.87)
icarus3 = device("icarus3",0.86)
#------------------------
dns = device("dns",0.85)
perfsonar1 = device("perfsonar1",0.84)
perfsonar2 = device("perfsonar2",0.83)	
'''	
'''
#Declare nodes	
root = node('Infrastructure',[virt,tor,ldap,vpn])
testbed_a = node('Openflow',[ocf,flowvisor,pronto])
testbed_b = node('Wireless',[omf])


netfpga1 = node('NetFPGA1',[netfpga1])
netfpga2 = node('NetFPGA2',[netfpga2])
netfpga3 = node('NetFPGA3',[netfpga3])

icarus1 = node('Icarus1',[icarus1])
icarus2 = node('Icarus2',[icarus2])
icarus3 = node('Icarus3',[icarus3])


#------------------------
accessories = node('Accesories',[])
dns = node('DNS',[dns])
measurement = node('Perfsonar',[perfsonar1,perfsonar2])
'''
'''
#Declare relationships
root.add_child(testbed_a)
root.add_child(testbed_b)
testbed_a.add_child(netfpga1)
testbed_a.add_child(netfpga2)
testbed_a.add_child(netfpga3)
testbed_b.add_child(icarus1)
testbed_b.add_child(icarus2)
testbed_b.add_child(icarus3)

accessories.add_child(measurement)
accessories.add_child(dns)
'''

