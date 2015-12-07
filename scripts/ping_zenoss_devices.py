#
#Pings Devices registered in zenoss

from fibreoss import common
from fibreoss import config
from fibreoss.api import zenoss
from fibreoss.agent import ping

#--------------------------------------------------------------
#INSTANTIATE ZENOSS API
#--------------------------------------------------------------
zenoss_api = zenoss.jsonapi()
#--------------------------------------------------------------
# Get devices from Zenoss
#--------------------------------------------------------------
rawdevices = zenoss_api.get_devices()

devices = []
devcount = rawdevices['totalCount']
print "Devices: " + str(devcount)
for dev in rawdevices['devices']:
	# Iterate through each device, and pull the rows we want
	#devices.append(fibreoss.api.zenoss.zendevice(dev['name'],dev['uid'],dev['productionState'],dev['ipAddressString']))
	device = common.device(dev['name'],dev['ipAddressString'])
	devices.append(device)
	
#ping agent expects to receive a list of devices as input
ping.ping(devices)

	
	

