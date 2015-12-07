from __future__ import division

import sys, getopt

import psql_conn_config as fibreoss_db

import datetime
import re

DEBUG = 1


#Node is the service
class node(object):
	def __init__(self, label='',devices=[]):
			self.label = label
			self.devices = devices
			self.children = []
	def add_child(self, obj):
			self.children.append(obj)
	def devices_avail(self):
			avail = []
			for device in self.devices:
					avail.append(device.availability)
			#print avail
			if avail == []:
				return 1.0
			else:
				return min(avail)
	def children_avail(self):
			sum=0
			for node in self.children:
					sum += node.node_avail()
			return sum/len(self.children)
	def node_avail(self):
			#print self.label
			#caso base:
			if not self.children:
					return self.devices_avail()
			#caso recursivo:
			else:
					return min(self.devices_avail(),self.children_avail())
	def affiliation(self,retrieve='parent'):
		affiliation = {}
		affiliation['openflow'] 	= 'infrastructure'
		affiliation['wireless'] 	= 'infrastructure'
		affiliation['netfpga\d*'] 		= 'openflow'
		affiliation['icarus\d*'] 		= 'wireless'
		affiliation['measurement']  = 'accessories'
		affiliation['dns'] 			= 'accessories'
		
		if retrieve == 'parent':
			for key in affiliation.keys():
				m = re.match(key, self.label)
				if m is not None:
					return affiliation[key]
		elif retrieve == 'children':
			child_list = []
			for key,value in affiliation.items():
				m = re.match(value, self.label)
				#if value in self.label:
				if m is not None:
					child_list.append(key)
			
			return child_list
		return None					
		

class device(object):
	def __init__(self, name="", availability=""):
		self.name = name
		self.availability = availability
		try:
			self.shortname = name.split('.')[0]
		except:
			pass
	def affiliation(self):
	
		regex = 'm.group(0)'
		
		affiliation = {}
		affiliation['virt'] 		= 'infrastructure'
		affiliation['tor'] 			= 'infrastructure'
		affiliation['ldap'] 		= 'infrastructure'
		affiliation['vpn'] 			= 'infrastructure'
		affiliation['ocf'] 			= 'openflow'
		affiliation['flowvisor'] 	= 'openflow'
		affiliation['pronto'] 		= 'openflow'
		affiliation['omf'] 			= 'wireless'
		affiliation['netfpga\d*']	= regex
		affiliation['icarus\d*'] 	= regex
		affiliation['dns'] 			= 'dns'
		affiliation['perfsonar\d*'] 	= 'measurement'
		
		for key in affiliation.keys():
			#if key in self.shortname:
			m = re.match(key, self.shortname)
			if m is not None:
				if affiliation[key] == regex:
					return eval(regex)
				else:
					return affiliation[key]
		
		return None

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
	


#------------------------------------------------------------------	
host='all'
#default is yesterday
date=datetime.datetime.now() + datetime.timedelta(days=(-1))
date= date.strftime('%Y-%m-%d')	
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
        date=a
	'''
	elif o == '-p':
		password=a
	elif o == '-d':
		days=int(a)
	'''
    else:
        print("Usage: %s -d <YYYY-mm-dd>" % sys.argv[0])
 #example
 #python requests_portal_ilha.py -H portal.uff.fibre.org.br -u <user> -p <pwd> [-n node1,node2,node3] 



#-------------------------------------------------------------------------------
cur = fibreoss_db.conn.cursor(cursor_factory=fibreoss_db.psycopg2.extras.DictCursor)
#Query para pegar os resultados de disponibilidade do dia na tabela zenoss_avail
query = "SELECT DISTINCT ON(device_text) device_text,timedelta_start,timedelta_end,availability,entry_time FROM zenoss_avail WHERE date_trunc('day',timedelta_start) = '"+date+"' ORDER BY device_text ASC,entry_time DESC;"
print query

try:
	cur.execute(query)
except:
	print "Database error"

#
# Note that below we are accessing the row via the column name.
result = cur.fetchall()


#close connection		
if fibreoss_db.conn:
	fibreoss_db.conn.close()
	

		
#Creates a dictionary of device object list. Each island has a key.
island_devices = {}
island_nodes = {}
for row in result:
	device_text = row['device_text']
	device_text = device_text.split('.')
	try:
		island = device_text[1]
	except:
		continue		
	
	island_devices[island] = []
	island_nodes[island] = {}

for row in result:
	#evdate = row['timedelta_start']
	#if date == evdate:
	#	avail_in_percent = "{:10.2f}".format(row['availability']*100)
	#	bgcolor = get_avail_color(row['availability'])
	device_text = row['device_text']
	availability = row['availability']
	
	device_text = device_text.split('.')
	try:
		island = device_text[1]
	except:
		continue
	#device_name = device_text[0]		
	
	#creates device object in island list
	island_devices[island].append(device(row['device_text'],availability))
	
	if DEBUG:
		print island + " " + row['device_text']
	
	

			

#Creates nodes dictionary
			
for island in island_devices:
	
	#Create node Accesories:
	if 'accessories' not in island_nodes[island]:
		island_nodes[island]['accessories'] = node('accessories',[])
	
	for device in island_devices[island]:
		#Declare nodes	

		node_name = device.affiliation()
		if node_name is None:
			continue
		
		if DEBUG:
			print device.name + " " + node_name
				
		#If the node does not exists, create node
		if node_name not in island_nodes[island]:
			island_nodes[island][node_name] = node(node_name,[])
		
		#Some nodes will have multiple instances (netfpga and icarus)
		#if node_name in ['netfpga','icarus']:
			
		
		#Append device to its node
		island_nodes[island][node_name].devices.append(device)


		


#Assigns relationships
for island in island_nodes.keys():
	for node_name in island_nodes[island].keys():
		
		print str(island) + " " + str(node_name)
		#parse dict through all nodes
		this_node = island_nodes[island][node_name]
		for child in this_node.affiliation('children'):
			
			
			#check if the node exists within the island and add it as child
			#if child in island_nodes[island].keys():
			for key in island_nodes[island].keys():
				m = re.match(child, key)
				if m is not None:
					child_node = island_nodes[island][key]
					this_node.add_child(child_node)
				
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
#Gera report em html
DAYS = 7 # A week

weekquery = timedelta(date + datetime.timedelta(days=-(DAYS-1)),date)
#Prepare the html file
html = (
"<table id='availability' class='display' cellspacing='0' width='100%' border='1'>\n"
"<thead>\n"
"<tr><th>Island</th><th>Description</th>"
)
for i in range(DAYS):
	curdate = weekquery.start + datetime.timedelta(days=i+1)
	html += "<th>"+str(curdate.strftime('%B-%d'))+"</th>"

html += (
"</tr>\n"
"</thead>\n"
"<tbody>\n"
)
for island in island_nodes.keys():
	
html += (
"</tbody>\n"
"</table>\n"
)
date = dayquery.start.strftime('%Y-%m-%d')
f = open(SAVE_PATH+'zenoss_week_avail_'+date+'.html','w')
f.write(html)
f.closed

'''
				
import code
code.interact(local=locals())		

			

		



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

