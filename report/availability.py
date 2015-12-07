
from fibreoss import common
from fibreoss import config

import sys, getopt
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
	for limit in config.AVAILABILITY_COLOR_CODE:
		try:
			if avail >= float(limit['min']):
				return(limit['color'])	
		except:
			return('gray')				

class federation(object):
	'''
	Calculates the availability of the federation
	Receives a datetime object
	'''

	def __init__(self, date=""):
		self.date = date
		self.island_devices = {}
		self.island_nodes = {}
	
	def init_dictionaries(self,devices):	
		'''
		Parses devices from queries and insert in dictionaries
		'''
		
		#ISLANDS DICTIONARY
		
		#Creates a dictionary of device object list. Each island has a key.
		#island_devices = {}
		#island_nodes = {}
		#for device in devices:
		#	island = device.island
		#	
		#	self.island_devices[island] = []
		#	self.island_nodes[island] = {}	
		
		for island in config.MONITORED_ISLANDS:
			self.island_devices[island] = []
			self.island_nodes[island] = {}	
			
	#def init_devices_dictionary(self,devices):
		
		#DEVICES DICTIONARY
		
		for device in devices:
			#evdate = row['timedelta_start']
			#if date == evdate:
			#	avail_in_percent = "{:10.2f}".format(row['availability']*100)
			#	bgcolor = get_avail_color(row['availability'])
			
			#creates device object in island list
			if device.island in config.MONITORED_ISLANDS:
				self.island_devices[device.island].append(device)
			
			if DEBUG:
				print device.island + " " + device.uri
				
	#def init_nodes_dictionary(self):
	
		#NODES DICTIONARY

	#Creates nodes dictionary		
		for island in self.island_devices:
			
			#Create node Accesories:
			if 'accessories' not in self.island_nodes[island]:
				self.island_nodes[island]['accessories'] = common.node('accessories',[])
			
			for device in self.island_devices[island]:
				#Declare nodes	

				node_name = device.affiliation()
				if node_name is None:
					continue
				
				if DEBUG:
					print device.uri + " " + node_name
						
				#If the node does not exists, create node
				if node_name not in self.island_nodes[island]:
					self.island_nodes[island][node_name] = common.node(node_name,[])
				
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
		
	
	
