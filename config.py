#/usr/bin/python2.4
#
#
'''

#------------------------------------------------------------
#ZENOSS API CONFIG
#------------------------------------------------------------
ZENOSS_INSTANCE = 'http://mon.fibre.org.br:8080'
ZENOSS_USERNAME = '<username>'
ZENOSS_PASSWORD = '<password>'

ZENOSS_ROUTERS = { 
		'MessagingRouter': 'messaging',
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
			
#------------------------------------------------------------
#MADDASH API CONFIG
#------------------------------------------------------------
MADDASH_INSTANCE = 'http://ps.fibre.org.br'
#MADDASH_USERNAME = ''
#MADDASH_PASSWORD = ''

#/maddash/grids/Loss
#/maddash/grids/One-way+Delay+BR
#/maddash/grids/One-way+Delay+EU-BR

MADDASH_GRIDS = ['Loss','One-way+Delay+BR','One-way+Delay+EU-BR']

#------------------------------------------------------------
#PING TEST CONFIG
#------------------------------------------------------------
    
# The number of workers.
NUM_WORKERS = 10
    
#------------------------------------------------------------
#OMF TEST CONFIG
#------------------------------------------------------------
DEFAULT_OFFSET_FOR_RESERVATION_DAYS = 7
ICARUS_NETWORK_BOOT_WAIT_TIME_MINUTES = 5
LSWEB_USERS = [
	{"island":"ufpe", "host":"portal.ufpe.fibre.org.br", "username":"<username>", "password":"<password>"},
	{"island":"uff", "host":"portal.uff.fibre.org.br", "username":"<username>", "password":"<password>"},
	{"island":"ufg", "host":"portal.ufg.fibre.org.br", "username":"<username>", "password":"<password>"},
	{"island":"ufrj", "host":"portal.ufrj.fibre.org.br", "username":"<username>", "password":"<password>"},
	{"island":"rnp", "host":"portal.rnp.fibre.org.br", "username":"<username>", "password":"<password>"}]

#------------------------------------------------------------
#REPORTS CONFIG
#------------------------------------------------------------
#Value tested must be greater than or equal the min value and will be tested in the order configured in the list
#MUST USE COLOR CODES OR THE MARKERS IN FEDERATION STATUS PAGA WONT APPEAR!
AVAILABILITY_COLOR_CODE = [
	{"min":"1.0","color":"#7CFC00"},#lawngreen 
	{"min":"0.9","color":"#FFFF00"},#yellow
	{"min":"0.7","color":"#FF8C00"},#darkorange
	{"min":"0.0","color":"#FF0000"}]#red

#SAVE_REPORT_PATH = "/var/www/datasources/"
SAVE_REPORT_PATH = "/home/fibreoss/python/report/"
REPORT_TEMPLATE_PATH = "/home/fibreoss/python/report/"
				
			
		
#------------------------------------------------------------
#COMMONS CONFIG
#------------------------------------------------------------
#RELATION OF SYSTEM DEVICES AND ITS PARENTS IN THE DEPENDENCY TREE		
SYSTEM_HIERARCHY = 	{
				"node":{
					"openflow"	:"infrastructure",
					"wireless"	:"infrastructure",
					"netfpga\d*"	:"openflow",
					"icarus\d*"	:"wireless",
					"measurement"	:"accessories",
					"dns"		:"accessories"
					},
				"device":{
					"virt"		:"infrastructure",
					"tor"		:"infrastructure",
					"ldap"		:"infrastructure",
					"vpn"		:"infrastructure",
					"ocf"		:"openflow",
					"flowvisor"	:"openflow",		
					"pronto"	:"openflow",
					"omf"		:"wireless",
					"netfpga\d*"	:"#REGEXMATCH",
					"icarus\d*"	:"#REGEXMATCH",
					"dns"		:"dns",
					"perfsonar\d*"	:"measurement"
				}
			}

MONITORED_ISLANDS = ['backbone','ufpa','ufpe','unifacs','rnp','noc','ufg','cpqd','ufrj','uff','usp','ufscar','ufrgs']
			
#------------------------------------------------------------
#
#------------------------------------------------------------



#------------------------------------------------------------
#
#------------------------------------------------------------
