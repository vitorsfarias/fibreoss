# Zenoss-4.x JSON API Example (python)
#
# To quickly explore, execute 'python -i api_example.py'
#
# >>> z = ZenossAPIExample()
# >>> events = z.get_events()
# etc.

import fibreoss.config



import json
import urllib
import urllib2



'''
ZENOSS_INSTANCE = 'http://mon.fibre.org.br:8080'
ZENOSS_USERNAME = 'guest'
ZENOSS_PASSWORD = 'guest'

ZENOSS_ROUTERS = { 'MessagingRouter': 'messaging',
			'EventsRouter': 'evconsole',
			'ProcessRouter': 'process',
			'ServiceRouter': 'service',
			'DeviceRouter': 'device',
			'NetworkRouter': 'network',
			'TemplateRouter': 'template',
			'DetailNavRouter': 'detailnav',
			'ReportRouter': 'report',
			'MibRouter': 'mib',
			'ZenPackRouter': 'zenpack' }
'''

class zendevice(object):
	def __init__(self, name=None, uid=None, productionstate=None,ipstring=None):
			self.name = name
			self.uid = uid
			self.productionstate = productionstate
			self.ipstring = ipstring
	def show(self):
		return str(self.name) + " " + str(self.uid) + " " + str(self.ipstring)

class jsonapi():
	def __init__(self, debug=False):
		"""
		Initialize the API connection, log in, and store authentication cookie
		"""
		# Use the HTTPCookieProcessor as urllib2 does not save cookies by default
		self.urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
		if debug: self.urlOpener.add_handler(urllib2.HTTPHandler(debuglevel=1))
		self.reqCount = 1

		# Contruct POST params and submit login.
		loginParams = urllib.urlencode(dict(
						__ac_name = fibreoss.config.ZENOSS_USERNAME,
						__ac_password = fibreoss.config.ZENOSS_PASSWORD,
						submitted = 'true',
						came_from = fibreoss.config.ZENOSS_INSTANCE + '/zport/dmd'))
		self.urlOpener.open(fibreoss.config.ZENOSS_INSTANCE + '/zport/acl_users/cookieAuthHelper/login',
							loginParams)

	def _router_request(self, router, method, data=[]):
		if router not in fibreoss.config.ZENOSS_ROUTERS:
			raise Exception('Router "' + router + '" not available.')

		# Contruct a standard URL request for API calls
		req = urllib2.Request(fibreoss.config.ZENOSS_INSTANCE + '/zport/dmd/' +
							  fibreoss.config.ZENOSS_ROUTERS[router] + '_router')

		# NOTE: Content-type MUST be set to 'application/json' for these requests
		req.add_header('Content-type', 'application/json; charset=utf-8')

		# Convert the request parameters into JSON
		reqData = json.dumps([dict(
					action=router,
					method=method,
					data=data,
					type='rpc',
					tid=self.reqCount)])

		# Increment the request count ('tid'). More important if sending multiple
		# calls in a single request
		self.reqCount += 1

		# Submit the request and convert the returned JSON to objects
		return json.loads(self.urlOpener.open(req, reqData).read())


	def get_devices(self, deviceClass='/zport/dmd/Devices', limit=1000):
		return self._router_request('DeviceRouter', 'getDevices', data=[{'uid': deviceClass,'limit': limit,'params': {} }])['result']
	
	def get_events(self, device=None, component=None, eventClass=None):
		data = dict(start=0, limit=100, dir='DESC', sort='severity')
		data['params'] = dict(severity=[5,4,3,2], eventState=[0,1])

		if device: data['params']['device'] = device
		if component: data['params']['component'] = component
		if eventClass: data['params']['eventClass'] = eventClass


		return self._router_request('EventsRouter', 'queryArchive', [data])['result']
	
	def get_current_events(self, device=None, component=None, eventClass=None, firstTime=None, lastTime=None):
		data = dict(start=0, limit=10000, dir='DESC', sort='severity')
		#data['params'] = dict(severity=[5,4,3,2], eventState=[0,1])
		data['params'] = dict(severity=[5])

		if device: 		data['params']['device'] 		= device
		if component: 	data['params']['component'] 	= component
		if eventClass: 	data['params']['eventClass'] 	= eventClass
		if firstTime: 	data['params']['firstTime'] 	= firstTime
		if lastTime: 	data['params']['lastTime'] 		= lastTime

		return self._router_request('EventsRouter', 'query', [data])['result']
	
	def get_events_history(self, device=None, component=None, eventClass=None, firstTime=None, lastTime=None):
		#eventState 0=New, 1=Ackknowledge, 2=Supressed
		#severity 0=clear, 1=Debug, 2 = Info, 3 = Warning, 4= Error, 5 = Critical
		
		data = dict(start=0, limit=10000, dir='DESC', sort='severity', archive=True)
		#data['params'] = dict(severity=[5,4,3,2,1,0], eventState=[0,1])
		data['params'] = dict(severity=[5])

		if device: data['params']['device'] = device
		if component: data['params']['component'] = component
		if eventClass: data['params']['eventClass'] = eventClass
		if firstTime: data['params']['firstTime'] = firstTime
		if lastTime: data['params']['lastTime'] 	= lastTime

		return self._router_request('EventsRouter', 'query', [data])['result']
	
	def add_device(self, deviceName, deviceClass):
		data = dict(deviceName=deviceName, deviceClass=deviceClass)
		return self._router_request('DeviceRouter', 'addDevice', [data])

	def create_event_on_device(self, device, severity, summary):
		if severity not in ('Critical', 'Error', 'Warning', 'Info', 'Debug', 'Clear'):
			raise Exception('Severity "' + severity +'" is not valid.')

		data = dict(device=device, summary=summary, severity=severity,
					component='', evclasskey='', evclass='')
		return self._router_request('EventsRouter', 'add_event', [data])
