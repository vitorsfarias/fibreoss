# JSON API Example (python)
#
# To quickly explore, execute 'python -i api_example.py'
#

import fibreoss


import json
import urllib
import urllib2

'''
MADDASH_INSTANCE = 'http://ps.fibre.org.br'
#MADDASH_USERNAME = 'guest'
#MADDASH_PASSWORD = 'guest'

#/maddash/grids/Loss
#/maddash/grids/One-way+Delay+BR
#/maddash/grids/One-way+Delay+EU-BR

GRIDS = ['Loss','One-way+Delay+BR','One-way+Delay+EU-BR']
'''
class MADDASHAPI():
	
	def __init__(self, debug=False):
		"""
		Initialize the API connection, log in, and store authentication cookie
		"""
		# Use the HTTPCookieProcessor as urllib2 does not save cookies by default
		self.urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
		if debug: self.urlOpener.add_handler(urllib2.HTTPHandler(debuglevel=1))
		self.reqCount = 1
		'''
		# Contruct POST params and submit login.
		loginParams = urllib.urlencode(dict(
						__ac_name = MADDASH_USERNAME,
						__ac_password = MADDASH_PASSWORD,
						submitted = 'true',
						came_from = MADDASH_INSTANCE + '/zport/dmd'))
		self.urlOpener.open(MADDASH_INSTANCE + '/zport/acl_users/cookieAuthHelper/login',
							loginParams)
		'''
		
	def _router_request(self, router, grid, data=[]):
		'''
		OK
		'''
	
		if grid and grid not in fibreoss.config.MADDASH_GRIDS:
			raise Exception('Grid "' + grid + '" not available.')

		# Contruct a standard URL request for API calls
		URL = fibreoss.config.MADDASH_INSTANCE + '/maddash/'
		if router:
			URL += router + '/'
		if grid:
			URL += grid + '/'
		req = urllib2.Request(URL)

		#return URL
		# NOTE: Content-type MUST be set to 'application/json' for these requests
		req.add_header('Content-type', 'application/json; charset=utf-8')

		# Convert the request parameters into JSON
		#reqData = json.dumps([dict(
		#			action=router,
		#			method=method,
		#			data=data,
		#			type='rpc',
		#			tid=self.reqCount)])

		# Increment the request count ('tid'). More important if sending multiple
		# calls in a single request
		self.reqCount += 1

		# Submit the request and convert the returned JSON to objects
		return json.loads(self.urlOpener.open(req).read())
	
	
	'''
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
	'''

'''
def main():
	print "MADDASH_API TEST PROCEDURE"
	z = MADDASHAPI()
	raw_events = z._router_request("grids","Loss",None)
	print raw_events
main()	
'''
