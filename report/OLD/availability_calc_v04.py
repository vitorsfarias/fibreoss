
from __future__ import division


#Node is the service
class node(object):
        def __init__(self, label='',devices=[]):
                self.label = label
                self.devices = devices
                self.children = []
        def add_child(self, obj):
                self.children.append(obj)
        def devices_avail(self):
                avail = []
                for device in self.devices:
                        avail.append(device.availability)
                #print avail
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

class device(object):
	def __init__(self, name="", availability=""):
		self.name = name
		self.availability = availability

def print_tree(node,level=0):
        for i in range(level):
                print "\t",
        print node.label
        for device in node.devices:
                for i in range(level):
                        print "\t",
                print "- <"+device.name+"("+str(device.availability)+")"+">"
        for child in node.children:
                print_tree(child,level+1)
	

	
#Query para pegar os resultados de disponibilidade do dia na tabela zenoss_avail
#SELECT device_text,timedelta_start,timedelta_end,availability,entry_time FROM zenoss_avail WHERE date_trunc('day',timedelta_start) = '2015-10-14';
	
	
	
#Declare devices
#Declare nodes	
#------------------------	
virt = device("virt",0.99)
tor = device("tor",0.98)
ldap = device("ldap",0.97)
vpn = device("vpn",0.96)
#------------------------
ocf = device("ocf",0.95)
flowvisor = device("flowvisor",0.94)
pronto = device("pronto",0.93)
netfpga1 = device("netfpga1",0.92)
netfpga2 = device("netfpga2",0.91)
netfpga3 = device("netfpga3",0.90)
#------------------------
omf = device("omf",0.89)
icarus1 = device("icarus1",0.78)
icarus2 = device("icarus2",0.87)
icarus3 = device("icarus3",0.86)
#------------------------
dns = device("dns",0.85)
perfsonar1 = device("perfsonar1",0.84)
perfsonar2 = device("perfsonar2",0.83)	
	
#Declare nodes	
root = node('Infrastructure',[virt,tor,ldap,vpn])
testbed_a = node('Openflow',[ocf,flowvisor,pronto])
testbed_b = node('Wireless',[omf])


netfpga1 = node('NetFPGA1',[netfpga1])
netfpga2 = node('NetFPGA2',[netfpga2])
netfpga3 = node('NetFPGA3',[netfpga3])

icarus1 = node('Icarus1',[icarus1])
icarus2 = node('Icarus2',[icarus2])
icarus3 = node('Icarus3',[icarus3])


#------------------------
accessories = node('Accesories',[])
dns = node('DNS',[dns])
measurement = node('Perfsonar',[perfsonar1,perfsonar2])

#Declare relationships
root.add_child(testbed_a)
root.add_child(testbed_b)
testbed_a.add_child(netfpga1)
testbed_a.add_child(netfpga2)
testbed_a.add_child(netfpga3)
testbed_b.add_child(icarus1)
testbed_b.add_child(icarus2)
testbed_b.add_child(icarus3)

accessories.add_child(measurement)
accessories.add_child(dns)



#----------------------------------------------------------------

print_tree(accessories)

#print availability(root)
print_tree(root)



print "\r\nnetfpga1\r\n"
print_tree(netfpga1)
print "netfpga1 Devices_AVAIL: " + str(netfpga1.devices_avail())



print "\r\ntestbed_a\r\n"
print_tree(testbed_a)
print "testbed_a Devices_AVAIL: " + str(testbed_a.devices_avail())
print "testbed_a Children_AVAIL: " + str(testbed_a.children_avail())
print "testbed_a NODE_AVAIL: " + str(testbed_a.node_avail())


print "\r\ntestbed_b\r\n"
print_tree(testbed_b)
print "testbed_b Devices_AVAIL: " + str(testbed_b.devices_avail())
print "testbed_b Children_AVAIL: " + str(testbed_b.children_avail())
print "testbed_b NODE_AVAIL: " + str(testbed_b.node_avail())


print "\r\nroot\r\n"
print_tree(root)
print "root Devices_AVAIL: " + str(root.devices_avail())
print "root Children_AVAIL: " + str(root.children_avail())
print "root NODE_AVAIL: " + str(root.node_avail())
