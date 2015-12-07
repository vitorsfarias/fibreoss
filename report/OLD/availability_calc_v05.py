from __future__ import division

import sys, getopt

import psql_conn_config as fibreoss_db

import datetime




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
			affiliation['Openflow'] 	= 'Infrastructure'
			affiliation['Wireless'] 		= 'Infrastructure'
			affiliation['NetFPGA'] 		= 'Openflow'
			affiliation['Icarus'] 		= 'Wireless'
			affiliation['Measurement']= 'Accessories'
			affiliation['DNS'] 			= 'Accessories'
			
			if retrieve == 'parent':
				for key in affiliation.keys():
					if key in self.label:
						return affiliation[key]
			elif retrieve == 'children':
				for key in affiliation.values():
					if key in self.label:
						return affiliation[key]

				
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

		affiliation = {}
		affiliation['virt'] 			= 'Infrastructure'
		affiliation['tor'] 			= 'Infrastructure'
		affiliation['ldap'] 			= 'Infrastructure'
		affiliation['vpn'] 			= 'Infrastructure'
		affiliation['ocf'] 			= 'Openflow'
		affiliation['flowvisor'] 	= 'Openflow'
		affiliation['pronto'] 		= 'Openflow'
		affiliation['omf'] 			= 'Wireless'
		affiliation['netfpga'] 	= 'NetFPGA'
		affiliation['icarus'] 		= 'Icarus'
		affiliation['dns'] 			= 'DNS'
		affiliation['perfsonar'] 	= 'PerfSonar'

		for key in affiliation.keys():
			if key in self.shortname:
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
	
	




def device_affiliation(name):

	affiliation = {}
	affiliation['virt'] 			= 'Infrastructure'
	affiliation['tor'] 			= 'Infrastructure'
	affiliation['ldap'] 			= 'Infrastructure'
	affiliation['vpn'] 			= 'Infrastructure'
	affiliation['ocf'] 			= 'Openflow'
	affiliation['flowvisor'] 	= 'Openflow'
	affiliation['pronto'] 		= 'Openflow'
	affiliation['omf'] 			= 'Wireless'
	affiliation['netfpga'] 	= 'NetFPGA'
	affiliation['icarus'] 		= 'Icarus'
	affiliation['dns'] 			= 'DNS'
	affiliation['perfsonar'] 	= 'PerfSonar'

	for key in affiliation.keys():
		if key in name:
			return affiliation[key]
	
	return None

def node_affiliation(name):

	affiliation = {}
	affiliation['Openflow'] 	= 'Infrastructure'
	affiliation['Wireless'] 		= 'Infrastructure'
	affiliation['NetFPGA'] 		= 'Openflow'
	affiliation['Icarus'] 		= 'Wireless'
	affiliation['Measurement']= 'Accessories'
	affiliation['DNS'] 			= 'Accessories'

	for key in affiliation.keys():
		if key in name:
			return affiliation[key]
	
	return None	


			

#Creates nodes dictionary
			
for island in island_devices:

	for device in island_devices[island]:
		#Declare nodes	

		node_name = device.affiliation('parent')
		if node_name is None:
			continue
		
		
		
		print device.name + " " + node_name
				
		#If the node does not exists, create node
		if node_name not in island_nodes[island]:
			island_nodes[island][node_name] = node(node_name,[])
		
		#Some nodes will have multiple instances (NETFPGA and ICARUS)
		#if node_name in ['NetFPGA','Icarus']:
			
		
		#Append device to its node
		island_nodes[island][node_name].devices.append(device)
	
import code
code.interact(local=locals())	


#Assigns relationships
for island in island_nodes.keys():
	for node_name in island_nodes[island].keys():
		print str(island) + " " + str(node)
		
	


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



#----------------------------------------------------------------

print_tree(accessories)

#print availability(root)
print_tree(root)



print "\r\nnetfpga1\r\n"
print_tree(netfpga1)
print "netfpga1 Devices_AVAIL: " + str(netfpga1.devices_avail())



print "\r\ntestbed_a\r\n"
print_tree(testbed_a)
print "testbed_a Devices_AVAIL: " + str(testbed_a.devices_avail())
print "testbed_a Children_AVAIL: " + str(testbed_a.children_avail())
print "testbed_a NODE_AVAIL: " + str(testbed_a.node_avail())


print "\r\ntestbed_b\r\n"
print_tree(testbed_b)
print "testbed_b Devices_AVAIL: " + str(testbed_b.devices_avail())
print "testbed_b Children_AVAIL: " + str(testbed_b.children_avail())
print "testbed_b NODE_AVAIL: " + str(testbed_b.node_avail())


print "\r\nroot\r\n"
print_tree(root)
print "root Devices_AVAIL: " + str(root.devices_avail())
print "root Children_AVAIL: " + str(root.children_avail())
print "root NODE_AVAIL: " + str(root.node_avail())
