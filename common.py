

import fibreoss

import paramiko
import sys
import re

#Node is the service
class node(object):
	def __init__(self, label='',devices=[],availability=None):
			self.label = label
			self.devices = devices
			self.children = []
			self.availability = availability
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

		affiliation = fibreoss.config.SYSTEM_HIERARCHY['node']
		
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
	def __init__(self, uri="", ipstring="", availability=None):
		self.uri = uri
		self.availability = availability
		self.ipstring = ipstring
		self.name = ''
		self.island = 'x'
		self.domain = 'x'
		
		try:
			'''
			An assumption is made here, all the tested hosts will have the name in the form:
			X.island.fibre.org.br, where fibre.org.br is the domain name
			'''
			self.name = uri.split('.')[0]
			array = uri.split('.')
			self.island = array[-4]
			self.domain = '.'.join(array[-3:])
		except:
			pass
		
	def affiliation(self):
	
		affiliation = fibreoss.config.SYSTEM_HIERARCHY['device']
		
		for key in affiliation.keys():
			#if key in self.shortname:
			m = re.match(key, self.name)
			
			if m is not None:
				regexmatch = m.group(0)
				if affiliation[key] == "#REGEXMATCH":
					return regexmatch
				else:
					return affiliation[key]
		
		return None
	
	def ssh_connect(self,username,password,command,hostname=None,port=22):
		
		if hostname == None:
			hostname = self.ipstring
		
		nbytes = 4096

		client = paramiko.Transport((hostname, port))
		client.connect(username=username, password=password)

		stdout_data = []
		stderr_data = []
		session = client.open_channel(kind='session')
		session.exec_command(command)
		while True:
			if session.recv_ready():
				stdout_data.append(session.recv(nbytes))
			if session.recv_stderr_ready():
				stderr_data.append(session.recv_stderr(nbytes))
			if session.exit_status_ready():
				break

		#print 'exit status: ', session.recv_exit_status()
		#print ''.join(stdout_data)
		#print ''.join(stderr_data)

		session.close()
		client.close()
		
		return (session.recv_exit_status(),stdout_data)




def ssh_connect(hostname,username,password,command,port=6622):



	nbytes = 4096


	client = paramiko.Transport((hostname, port))
	client.connect(username=username, password=password)

	stdout_data = []
	stderr_data = []
	session = client.open_channel(kind='session')
	session.exec_command(command)
	while True:
		if session.recv_ready():
			stdout_data.append(session.recv(nbytes))
		if session.recv_stderr_ready():
			stderr_data.append(session.recv_stderr(nbytes))
		if session.exit_status_ready():
			break

	#print 'exit status: ', session.recv_exit_status()
	#print ''.join(stdout_data)
	#print ''.join(stderr_data)


	session.close()
	client.close()
	
	return (session.recv_exit_status(),stdout_data)
 
#--------------------------------------------------------

def island_and_domain(host):
	#An assumption is made here, all the tested hosts will have the name in the form:
	#X.island.fibre.org.br, where fibre.org.br is the domain name
	try:
		array = host.split('.')
		island = array[-4]
		domain = '.'.join(array[-3:])
	except:
		island = 'x'
		domain = 'x'
	finally:
		return(island,domain)
		

 
 





