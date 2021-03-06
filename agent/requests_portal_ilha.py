#!/usr/bin/env python
# -*- coding: cp1252 -*-

#
#
#

import fibreoss


import datetime
import os

import requests

from BeautifulSoup import BeautifulSoup
import re

import sys, getopt
import time

import traceback

#DB connect
import json


#import psql_conn_config as fibreoss_db
 

#--------------------- 





#Alguns portais esperam receber o tempo em UTC: (ufpe por exemplo) O portal da uff recebe o tempo em BRT
# O current server time � igual, no caso
#S� o servidor da UFF estava com a configura��o de hora errada. Todos est�o em UTC

class lsweb(object):


	# Store input and output file names
	days = ''#fibreoss.config.DEFAULT_OFFSET_FOR_RESERVATION_DAYS
	host = ""
	island = ""
	domain = ""
	username = ""
	password = ""
	
	reservationtime = None
	reservation_payload = {}
	
	#is a global
	current_server_time = None
	#AGENT_NAME = os.path.dirname(os.path.realpath(__file__)) + "/" + __file__
	AGENT_NAME = __file__ 
	#TEST_NAME = "OMF_RESERVATION"
	
	nodeips = None

	_session_ = None
	_database_ = None
	
	def __init__(self):
	
		self._database_ = fibreoss.db.fibreoss()
		self._session_ = requests.Session()
	
	def disable_security_warnings(self):
		requests.packages.urllib3.disable_warnings()
	
	def connect(self,host,username,password):
		self.host=host
		self.username=username
		self.password=password
	
		(self.island,self.domain) = fibreoss.common.island_and_domain(host)
	
	
	
		
		# Fill in your details here to be posted to the login form.
		auth_payload = {
		    'username': self.username,
		    'password': self.password,
		    'sbmt_login': 'Log+in'
		}
		header = {
		    #'Host': 'portal.uff.fibre.org.br',
		    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:40.0) Gecko/20100101 Firefox/40.0',
		    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		    'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
		    #'Referer': 'https://portal.uff.fibre.org.br/LS-WEB/index.php',
		    'Connection': 'keep-alive'
		}

		print "#----------------------------------------"
		print datetime.datetime.now()
		print self.host
		print "#----------------------------------------"
	
		#with requests.Session() as s:

		###################################################
		#RESERVATION
		###################################################
		#login
		try:
			p = self._session_.post('https://'+self.host+'/LS-WEB/index.php', data=auth_payload, verify=False)

		except Exception, e:
			traceback.print_exc()
			print e
			#e = "exception"
			subject_url = 'ls-web.webservices.omf.'+self.island+'.'+self.domain
			insert_values = ("OMF_RESERVATION",'',self.host,"ERROR: " + str(e),'now()',self.AGENT_NAME,subject_url,1,10001)

			self._database_.insert_omf_test(insert_values)
			#sys.exit(1)
			return(1)


		#except requests.exceptions.Timeout:
		#	# Maybe set up for a retry, or continue in a retry loop
		#except requests.exceptions.TooManyRedirects:
		#	# Tell the user their URL was bad and try a different one
		#	print "TooManyRedirects"
		#	sys.exit(1)
		#	
		#except requests.exceptions.RequestException as e:
		#	# catastrophic error. bail.
		#	print e
		#	sys.exit(1)



		if not p.status_code == requests.codes.ok:
			print "Host returned: " + p.status_code
			subject_url = 'ls-web.webservices.omf.'+self.island+'.'+self.domain
			insert_values = ("OMF_RESERVATION",'',self.host,"Host returned: " + str(p.status_code),'now()',self.AGENT_NAME,subject_url,1,10002)
			self._database_.insert_omf_test(insert_values)
			#exit(1)
			return(1)



		#insert_values = "'"+TEST_NAME+"','"+str(reservation_payload)+"','"+self.host+"','-','no events found',now(),"+"'"+self.AGENT_NAME+"'"
		#insert_values = (TEST_NAME,str(reservation_payload),self.host,'-','now()',self.AGENT_NAME)
		#self._database_.insert_omf_test(insert_values)
		return(0)

		#---------------------------------------------------------------
	def set_reservation_offset_days(self,days):
		#reserve time is now + 1 year?
		#the reservation nodes are all the available nodes. If no nodes are available, the script will try another time
		#now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		#startdt = datetime.datetime.strptime( parastartdate, "%Y-%m-%d %H:%M:%S" )
		self.reservationtime = datetime.datetime.now() + datetime.timedelta(days=days)

		#reservation time must be UTC and the server has to be in UTC timezone
		#reservationtime = reservationtime + datetime.timedelta(hours=2)
		
		month = self.reservationtime.strftime('%m')
		year = self.reservationtime.strftime('%Y')
		day = self.reservationtime.strftime('%d')
		hour = self.reservationtime.strftime('%H')

		self.reservation_payload = {
			'start': year+"-"+month+"-"+day+" "+hour+":00:00",
			'end': year+"-"+month+"-"+day+" "+hour+":30:00",
			'reserve': "true",
			'book_resources[]': []
		}
		
		return(0)
	
	def set_reservation_time(self,year,month,day,hour,minute,second='00'):
		#reserve time is now + 1 year?
		#the reservation nodes are all the available nodes. If no nodes are available, the script will try another time
		#now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		#startdt = datetime.datetime.strptime( parastartdate, "%Y-%m-%d %H:%M:%S" )
		timestr = year+'-'+month+'-'+day+' '+hour+':'+minute+':'+second
		self.reservationtime = datetime.datetime.strptime( timestr, "%Y-%m-%d %H:%M:%S" )
	
		return(0)
				
	def check_available_nodes(self):
	
		month = self.reservationtime.strftime('%m')
		year = self.reservationtime.strftime('%Y')
		day = self.reservationtime.strftime('%d')
		hour = self.reservationtime.strftime('%H')

		checknodes_payload = {
		    'start_date': year+"-"+month+"-"+day,
		    'shour': hour,
		    'smin': "00",
		    #'duration': "0.5"
		    'duration': "1"
		}
	
	    			
		#Check Available nodes
		p = self._session_.post('https://'+self.host+'/LS-WEB/index.php?page=reservation&m='+month+'&y='+year+'/', data=checknodes_payload, verify=False)
		data = p.text
		#soup = BeautifulSoup(data)
		#print soup.prettify()

		#get the current server time
		match = re.findall(r"Current Server Time: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", data)
		try:
			self.current_server_time = datetime.datetime.strptime( match[0], "%Y-%m-%d %H:%M:%S" )
		except:
			#No nodes are available
			print "Could not Determine Server Local Time"

			subject_url = 'ls-web.webservices.omf.'+self.island+'.'+self.domain
			insert_values = ("SERVER_LOCAL_TIME_RETRIEVAL",'Searching for: Current Server Time: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',self.host,'Could not Determine Server Local Time','now()',self.AGENT_NAME,subject_url,1,10009)
			self._database_.insert_omf_test(insert_values)
			#my best guess in case of fail
			self.current_server_time = datetime.datetime.now() - datetime.timedelta(hours=2)

		print "current server time: "+ str(self.current_server_time)
	    
	    
		#icarus14: <input type='checkbox' name='book_resources[]' value='22' />
		match = re.findall(r"([^>]+): <input type='checkbox' name='book_resources\[\]' value='(\d+)' />", data)
		print "Available Nodes: "+str(match)

		if not match:
			#No nodes are available
			print "No nodes are available"

			subject_url = 'reservation.ls-web.webservices.omf.'+self.island+'.'+self.domain
			insert_values = ("OMF_RESERVATION",str(self.reservation_payload),self.host,'No nodes are available','now()',self.AGENT_NAME,subject_url,2,10003)
			self._database_.insert_omf_test(insert_values)
			return(2)

		for node in match: 
			self.reservation_payload['book_resources[]'].append(node[1])
			print node[0]+" is "+node[1]

		print "Parameters for reservation request: "+str(self.reservation_payload)
		
		return(0)
    
	def make_reservation(self):
	
		month = self.reservationtime.strftime('%m')
		year = self.reservationtime.strftime('%Y')
	
		#-------------------------------------------------------------------------
		#Make a reservation
		p = self._session_.post('https://'+self.host+'/LS-WEB/index.php?page=reservation&m='+month+'&y='+year+'/', data=self.reservation_payload, verify=False)

		data = p.text

		match = re.findall(r"<div id='message' class='(\w+)'><span></span><a>([\w\s!]+)</a></div>", data)
		print match
		subject_url = 'reservation.ls-web.webservices.omf.'+self.island+'.'+self.domain
		insert_values = ("OMF_RESERVATION",str(self.reservation_payload),self.host,match,'now()',self.AGENT_NAME,subject_url,0,10004)
		self._database_.insert_omf_test(insert_values)

		#--------------------------------------------------
		
		return (0)
		
	def check_reservation(self,booked_reservation_time=None):
		###################################################
		#NODE TEST
		###################################################	
		
		if booked_reservation_time is None:
			print "checking reservation for current server local time: "+self.current_server_time.strftime('%Y-%m-%d %H:%M:%S')
			booked_reservation_time = self.current_server_time

		# Check reservations
		r = self._session_.get('https://'+self.host+'/LS-WEB/index.php?page=my_reservations')
		data = r.text
		soup = BeautifulSoup(data)
		#print soup.prettify()

		#reservations = soup.find("table", {"id": "reservation_resources"})

		tables = soup.findChildren('table')
		my_table = tables[1]

		rows = my_table.findChildren(['th', 'tr'])
		for row in rows:
			cells = row.findChildren('td')
	
	
			#print str(cells[1]) + " " + str(cells[2])
			date = re.compile(r'<td>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}</td>')
			if (date.match(str(cells[1])) and date.match(str(cells[2]))) is not None:
			#if (date.match(cells[1].string)) is not None:
				#print "Reserves: " + cells[1].string + " to " + cells[2].string
				startdt = datetime.datetime.strptime( cells[1].string, "%Y-%m-%d %H:%M:%S" )
				enddt = datetime.datetime.strptime( cells[2].string, "%Y-%m-%d %H:%M:%S" )
				if startdt <= booked_reservation_time and  enddt > booked_reservation_time:
					print "Testing reservation: " + str(cells[0])
			
			
					if len(cells) < 3:
						#only for current date reservation
						#NO nodes are available
						print "There are no nodes available"
						subject_url = 'reservation.ls-web.webservices.omf.'+self.island+'.'+self.domain
						insert_values = ("OMF_RESERVATION",'',self.host,'Portal shows no reserved nodes','now()',self.AGENT_NAME,subject_url,1,10005)
						self._database_.insert_omf_test(insert_values)
						#exit(0)
						return (1)
			
			

					match = re.findall(r'<input type="submit" value="Details" onclick="showReservationDetails\((\d+)\)"', str(cells[3]))
					reservation_details = soup.find("tr", {"id": "reservation_details_"+str(match[0])})
			
					self.nodeips = re.findall(r'<b>Control IP:</b>[ ]*([\d\. ]+)', str(reservation_details))
					#nodehrn = re.findall(r'<b>HRN:</b>[ ]*([\d\. ]+)', str(reservation_details))
					#I think all this webscrap should be replaced by an omf tell command
					
		if self.nodeips is None:
			print 'Could not find any reservation for the time informed: '+booked_reservation_time.strftime('%Y-%m-%d %H:%M:%S') 
			
			return(1)
		else:
			return(0)
		
	def icarus_network_boot(self):
		###################################################
		#TURN ON NODE
		###################################################	

		#import code
		#code.interact(local=locals())	

		try:
			self.nodeips
		except NameError:
		#There is no Reservation
			print "There is no reservation"
			subject_url = 'reservation.ls-web.webservices.omf.'+self.island+'.'+self.domain
			insert_values = ("OMF_RESERVATION",'',self.host,'There is no reservation','now()',self.AGENT_NAME,subject_url,1,10006)
			self._database_.insert_omf_test(insert_values)
			#exit(0)
			return(1)
		else:
			print "IPs: " + str(self.nodeips)



		#islandname = self.host.split(".")[1]
		ssh_user = self.username+'@'+self.island
		password = self.password

		#Turn on nodes
		#wrong name on purpose to get the reserved nodes hrn
		command = 'omf tell -t hrn'
		response = fibreoss.common.ssh_connect(self.host,ssh_user,password,command)
		A = str(response[1])
		lines = A.split("\\n")

		print command
		for line in lines:
			print line + " " + str(line.startswith('omf'))
	
			if line.startswith('omf'):
				command = "omf tell -a on -t "+line
				print command
		
				#GET node name:
				try:
					array = line.split('.')
					node_name = array[-1]
				except:
					node_name = 'x'
		
				omf_tell = fibreoss.common.ssh_connect(self.host,ssh_user,password,command)
		
				if re.findall(r'FATAL', str(omf_tell[1])) is not None:
					print "A FATAL error occurred"
			
					non_decimal = re.compile(r'[^\d]+')
					node_number = non_decimal.sub('', node_name)
			
					#TODO: os nomes devem ser padronizados? Fa�o a suposi��o aqui de que o nome do n� sempre ser� icarus e o final do IP. Essa � a regra que consta no wiki da rnp
					#Por enquanto todos os n�s do omf ser�o chamados de icarus. Aqui eu for�o esse nome.
					#subject_url = 'cmc'+'.'+node_name+'.'+island+'.'+domain
					#instead of using an arbitrary node name set by operator, will use an standard device name: icarus
					subject_url = 'networkboot.icarus'+node_number+'.'+self.island+'.'+self.domain
					insert_values = ("OMF_NODE_TEST",response,self.host,'A FATAL error occurred while trying to turn ON the node: '+line,'now()',self.AGENT_NAME,subject_url,1,10007)
					self._database_.insert_omf_test(insert_values)
			if line == 'The nodes your command is using:':
				break



		#Time to let the nodes wake up
		wait = fibreoss.config.ICARUS_NETWORK_BOOT_WAIT_TIME_MINUTES
		print "WILL WAIT "+str(wait)+" MINUTES FOR THE NODES TO BOOT" 
		time.sleep(60*wait)
		
		return (0)
	def ping_nodes(self):
		
		ssh_user = self.username+'@'+self.island
		password = self.password
		
	
		#Test reserved nodes
		command1 = ''
		command2 = ''
		for ip in self.nodeips:
			#octets = ip.split(".")
			#cmc_ip = "172.16."+octets[1]+"."+octets[3]
			control_ip = ip
			#command1 = "wget 'http://"+cmc_ip+"/on';"
			command2 = "ping -c 2 "+control_ip+";"


			#try to turn on node again
			#print "Turn on node: "+command1
			#wget_response = ssh_connect(self.host,ssh_user,password,command1)
			#print wget_response[1]
	
	
			#ping node
			print "Ping node: "+command2
			ping_response = fibreoss.common.ssh_connect(self.host,ssh_user,password,command2)
			#print ping_response[1]
	
			#Assuming the node name is: 'icarus' plus number of the last octet
			try:
				node_number = control_ip.split('.')[-1]
			except:
				node_number = 'x'	
	
			if ping_response[0] == 0:
			#Ping OK
				print control_ip + ' is UP'
				subject_url = 'control.network.icarus'+node_number+'.'+self.island+'.'+self.domain
				insert_values = ("OMF_NODE_TEST",ping_response,self.host,control_ip + ' is UP','now()',self.AGENT_NAME,subject_url,0,10008)
			elif ping_response[0] == 1:
			#ping NOK
				print control_ip + ' is DOWN'
				subject_url = 'control.network.icarus'+node_number+'.'+self.island+'.'+self.domain
				insert_values = ("OMF_NODE_TEST",ping_response,self.host,control_ip + ' is DOWN','now()',self.AGENT_NAME,subject_url,1,10008)
			self._database_.insert_omf_test(insert_values)
		return(0)
	
	
    #import code
    #code.interact(local=locals())

	
	#Aflter the reservation check, the script will access the omf portal
    
    #remove reservations?
    #curl 'https://portal.uff.fibre.org.br/LS-WEB/index.php?page=my_reservations' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3' -H 'Connection: keep-alive' -H 'Cookie: PHPSESSID=oq6irqflsp2nkflfkfv8rbk3l3' -H 'Host: portal.uff.fibre.org.br' -H 'Referer: https://portal.uff.fibre.org.br/LS-WEB/index.php?page=my_reservations' -H 'User-Agent: Mozilla/5.0 (Windows NT 6.1; rv:40.0) Gecko/20100101 Firefox/40.0' -H 'Content-Type: application/x-www-form-urlencoded' --data 'reservation_id=56&cancel_reservation=Remove'

#if self.ENABLE_PSQL:   
#	#close DB connection		
#	if fibreoss_db.conn:
#		fibreoss_db.conn.close()   

