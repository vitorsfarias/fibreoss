#!/usr/bin/python
# Perfsonar control script
#
# 
#


import maddash_api
import json
import argparse

import hashlib  #To generate an uid for the perfsonar events
import base64	#


#raw_events = z._router_request("grids","Loss",None)
def parse_maddash_json(router,grid):
	'''
	Get grids 					/maddash/grids
	Get single grid  			/maddash/grids/<grid-name>
	Get dashboards				/maddash/dashboards
	'''

	z = maddash_api.MADDASHAPI()
	raw_events = z._router_request(router,grid,None)
	
	
	out_table = []
	for i,row in enumerate(raw_events['grid'],start=0):
		#print raw_events['rows'][i]
		for j,cell in enumerate(row,start=0):
			#evid,source,sink,message,status,prevCheckTime,uri
			out_line = {}
			
			#print "Source: " + raw_events['rows'][i]['name'] + " Sink: " + raw_events['columnNames'][j]
			out_line['source']=raw_events['rows'][i]['name']
			out_line['sink']=raw_events['columnNames'][j]
			#Will skip null cells
			if cell is not None:
				#Dont know why, but the cell object is a single element list with a python object inside as string
				data = eval(str(cell[0]))
				
				#print data['message']
				out_line['message'] = data['message']
				out_line['status'] = data['status']
				out_line['prevchecktime'] = data['prevCheckTime']
				out_line['grid'] = grid
				out_line['uri'] = data['uri']
				#Using the previous checktime wont work because maddash constalty changes it. And there is no start time :(. Damn it Maddash
				#string_key = str(data['prevCheckTime']) +  str(out_line['source']) +  str(out_line['sink'])
				string_key = str(grid) + str(out_line['source']) +  str(out_line['sink'])
				out_line['evid']= base64.urlsafe_b64encode(hashlib.md5(string_key).digest())
			
				out_table.append(out_line)
		
	#print json.dumps(out_table, indent=4, sort_keys=False)
	return json.dumps(out_table)
	



#Argument parser
parser = argparse.ArgumentParser(description='Event Grabber from perfsonar API')
parser.add_argument('-r','--router', help='router (e.g. grids,maddash)',required=True)
parser.add_argument('-g','--grid',help='grids (e.g. Loss, Throughput)', required=False)
args = parser.parse_args()
	
## show values ##
#print ("Router: %s" % args.router )
#print ("Grid: %s" % args.grid )


print (parse_maddash_json(args.router,args.grid))

