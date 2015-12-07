
from fibreoss import db
from fibreoss import common
from fibreoss import report
from fibreoss import config

import datetime
#from jinja2 import Template

import pprint
pp = pprint.PrettyPrinter(indent=4)

database = db.fibreoss()
wr = report.table_simple('availability',['Islands'])


date = datetime.datetime.strptime("2015-12-03","%Y-%m-%d")

#Gera dict para report em html
DAYS = 20 # A week
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

htmlcontent = wr.export('html')

#pp.pprint(wr.table)
#pp.pprint(wr.style)

#import code
#code.interact(local=locals())	


str_date=date.strftime('%Y-%m-%d')
if DAYS == 1: 	
	rpname = '_day_'
elif DAYS == 1:
	rpname = '_week_'
else:
	rpname = '_'
f = open(config.SAVE_REPORT_PATH+'islands_avail/islands'+rpname+'avail_'+str_date+'.html','w')
f.write(htmlcontent)
f.close()


