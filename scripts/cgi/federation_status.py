#!/usr/bin/python

#print "Content-type: text/html\n"
print "Content-type: application/json"
print

from fibreoss import db
from fibreoss import common
from fibreoss import report
from fibreoss import config

import json
import datetime
#from jinja2 import Template

import pprint
pp = pprint.PrettyPrinter(indent=4)

database = db.fibreoss()
wr = report.table_simple('availability',['Islands'])


date = datetime.datetime.strptime("2015-12-03","%Y-%m-%d")

#Gera dict para report em html
DAYS = 7 # A week
startdate = date - datetime.timedelta(days=DAYS)

#generate table with week results
for i in range(DAYS):
	curdate = startdate + datetime.timedelta(days=i+1)
	str_curdate = curdate.strftime('%Y-%m-%d')
	
	
	result = database.fetch_zenoss_avail(curdate)
	devices=[]
	for row in result:
		device = common.device(row['device_text'],"",row['availability'])
		devices.append(device)
	
	#report.availability_report(date)
	daily_report = report.availability.federation()
	daily_report.init_dictionaries(devices)
	
	if str_curdate not in wr.report.keys():
		wr.report[str_curdate] = {}


	for island in daily_report.island_nodes.keys():
		#print '--------------------------------------------------------'
		#print str_curdate + '\t' + island
		#print '--------------------------------------------------------'
		if 'infrastructure' in daily_report.island_nodes[island].keys():
			root = daily_report.island_nodes[island]['infrastructure']
			#print "Infrastructure AVAIL: " + str(root.node_avail())
			if island not in wr.report[str_curdate].keys():
				wr.report[str_curdate][island] = {}
			
			wr.report[str_curdate][island] = root.node_avail()

#pp.pprint(wr.report)



jsoncontent = wr.export('json')

#pp.pprint(wr.table)
#pp.pprint(wr.style)

	

#Calculate average availability
STATUS = {}
'''
Imitate this php array
$marker_info = array(
'uff.fibre.org.br'=>array('color'=>'ff0000','availability'=>'0,00%','events'=>'25'),
'ufpe.fibre.org.br'=>array('color'=>'00ff00','availability'=>'94,00%','events'=>'25'),
'ufg.fibre.org.br'=>array('color'=>'00ff00','availability'=>'100,00%','events'=>'25'),
'usp.fibre.org.br'=>array('color'=>'00ff00','availability'=>'99,00%','events'=>'25'),
'ufrj.fibre.org.br'=>array('color'=>'00ff00','availability'=>'80,00%','events'=>'2'),
'ufpa.fibre.org.br'=>array('color'=>'ff0000','availability'=>'0,00%','events'=>'25'),
'unifacs.fibre.org.br'=>array('color'=>'ff0000','availability'=>'0,00%','events'=>'10'),
'ufscar.fibre.org.br'=>array('color'=>'00ff00','availability'=>'90,00%','events'=>'25'),
'rnp.fibre.org.br'=>array('color'=>'00ff00','availability'=>'100,00%','events'=>'1'),
'cpqd.fibre.org.br'=>array('color'=>'ff0000','availability'=>'0,00%','events'=>'1'),
'ufrgs.fibre.org.br'=>array('color'=>'cccccc','availability'=>'-','events'=>'0')
);
'''

#data = json.load(jsoncontent) #is actually a list of json

islandlist = eval(jsoncontent)
for row in islandlist:
	avail_list = []
	islanduri = ''
	for key,value in row.items():
		if key == 'Islands':
			island = value
			#TODO:change report object to also use uri as key
			islanduri = island + '.fibre.org.br'
			if islanduri not in STATUS.keys():
				STATUS[islanduri] = {}
		else:
			try:
				avail_list.append(float(value))
			except:
				pass

	average_avail = sum(avail_list)/len(avail_list)

	avail_str = "{:10.2f}".format(average_avail)
	avail_color = report.availability.get_avail_color(average_avail)
	STATUS[islanduri] = {'color':avail_color,'availability':avail_str,'events':''}


#import code
#code.interact(local=locals())


response=STATUS
jsonresponse = (json.JSONEncoder().encode(response))
print jsonresponse



