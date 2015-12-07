
import availability

from fibreoss import config


import datetime
from jinja2 import Template
import json

class table_simple(object):
	report = {}
	header = []
	style = []
	table = []
	table_id = ''
		
	def __init__(self,id,header):
		self.table_id = id
		self.header = header
		
	def export(self,type):
	
		days = self.report.keys()
		days.sort()
		days_str=[]
		for day in days:
			curdate = datetime.datetime.strptime(day,"%Y-%m-%d")
			days_str.append(str(curdate.strftime('%B-%d')))
		
		nodes = []
		for day in self.report:
			#a unique set of nodes in all days
			nodes = list(set(nodes) | set(self.report[day].keys()))	
		
		
		
		self.header = self.header+days_str

		self.table = []
		self.style = []
		for node in nodes:
			table_row = {}
			style_row = {}
			
			table_row[self.header[0]] = node
		
			for day in days:
				
				curdate = datetime.datetime.strptime(day,"%Y-%m-%d")
				day_str = str(curdate.strftime('%B-%d'))

				if node in self.report[day]:
					nodeavail = self.report[day][node]
					avail_str = "{:10.2f}".format(nodeavail*100)
					style = "background-color:"+availability.get_avail_color(nodeavail)+";"
					
					table_row[day_str] = avail_str
					style_row[day_str] = style
				else:
					table_row[day_str] = '-'
					style_row[day_str] = ''
					
			
			self.table.append(table_row)
			self.style.append(style_row)
		
		if type == 'html':
			if len(days) == 1:
				file = open(config.REPORT_TEMPLATE_PATH+'template_day_minimal.html', 'r')
			else:
				file = open(config.REPORT_TEMPLATE_PATH+'template_week_minimal.html', 'r')
			template = Template(file.read())
			file.close()
			data = template.render(id=self.table_id,dict=self.table,style=self.style,header=self.header)
			return data
		elif type == 'json':
			data = json.JSONEncoder().encode(self.table)
			return data
		
