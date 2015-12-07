#Test omf web interface using fibreoss test agent
#

from fibreoss import common
from fibreoss import config
from fibreoss.agent import omf 




agent = omf.lsweb()
conn_info = config.LSWEB_USERS
agent.disable_security_warnings()
agent.connect(conn_info[2]['host'],conn_info[2]['username'],conn_info[2]['password'])
agent.set_reservation_offset_days(1)
agent.check_available_nodes()
#agent.make_reservation()
agent.check_reservation()
#agent.icarus_network_boot()
agent.ping_nodes()

