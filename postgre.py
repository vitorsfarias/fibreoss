#/usr/bin/python2.4
#
#

#-----------------------------------------------------------
# CONNECT TO POSTGRE SQL
#-----------------------------------------------------------
# load the adapter
import psycopg2
import sys

# load the psycopg extras module
import psycopg2.extras



class fibreoss(object):
	_db_connection = None
	_db_cur = None

	def __init__(self):
		#self._db_connection = db_module.connect('host', 'user', 'password', 'db')
		#self._db_cur = self._db_connection.cursor()
        	# Try to connect
		try:
		    self._db_connection = psycopg2.connect("dbname='fibreoss' user='<username>' password='<password>'")
		except:
		    print "Unable to connect to the database."
		    
		self._db_cur = self._db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
		#Init connection

	def query(self, query, params):
		return self._db_cur.execute(query, params)
	
	
	def insert_ping_test(self,insert_values):
	#-------------------------------------------------------------
	#INSERT TO DATABASE
		try:
			self._db_cur.execute("INSERT INTO ping_tests("
			"test_name,test_parameters,test_subject,test_results,test_time,agent,test_subject_url,return_code,test_id"
			") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",insert_values)
			self._db_connection.commit()
		
		except psycopg2.DatabaseError, e:
		
			if self._db_connection:
				self._db_connection.rollback()
		
			print 'Error %s' % e	
			#sys.exit(1)	
	#--------------------------------------------------------
	def insert_omf_test(self,insert_values):	
	#-------------------------------------------------------------
		#INSERT TO DATABASE
		try:
			self._db_cur.execute("INSERT INTO omf_tests("
			"test_name,test_parameters,test_subject,test_results,test_time,agent,test_subject_url,return_code,test_id"
			") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",insert_values)
			self._db_connection.commit()
		
		except psycopg2.DatabaseError, e:
		
			if self._db_connection:
				self._db_connection.rollback()
		
			print 'Error %s' % e    
			#sys.exit(1)
		
	#--------------------------------------------------------
	def fetch_zenoss_avail(self,date):
		"""
		Gets availability results from zenoss_avail table
		Receives a datetime event as input
		"""		
	#-------------------------------------------------------------------------------
		#Query para pegar os resultados de disponibilidade do dia na tabela zenoss_avail
		str_date=date.strftime('%Y-%m-%d')	
		#query = "SELECT DISTINCT ON(device_text) device_text,timedelta_start,timedelta_end,availability,entry_time FROM zenoss_avail WHERE date_trunc('day',timedelta_start) = '"+str_date+"' ORDER BY device_text ASC,entry_time DESC;"


		#SELECT FROM DATABASE
		try:
			self._db_cur.execute("SELECT DISTINCT ON(device_text) device_text,timedelta_start,timedelta_end,availability,entry_time FROM zenoss_avail WHERE date_trunc('day',timedelta_start) = '"+str_date+"' ORDER BY device_text ASC,entry_time DESC;")
			self._db_connection.commit()
		
		except psycopg2.DatabaseError, e:
		
			if self._db_connection:
				self._db_connection.rollback()
		
			print 'Error %s' % e    
			#sys.exit(1)
		
		result = self._db_cur.fetchall()
		return result
		#--------------------------------------------------------
	def fetch_current_events(self):
		"""
		Shows events from the current day on the tables: omf_tests, ocf_tests and ping_tests.
		Human readable and showing only one event per test_subject_url
				
		THIS IS THE VIEW QUERY. JUST FOR REFERENCE
		--current events view query
		SELECT DISTINCT ON(A.test_subject_url) A.ocf_tests_id id,A.test_time,A.test_subject_url,D.string return,C.name event_level,A.test_id FROM ocf_tests A INNER JOIN events_info B ON (A.test_id = B.test_id) AND (A.return_code = B.return_code) INNER JOIN event_return_codes D ON A.return_code = D.code INNER JOIN event_levels C ON B.event_level = C.id WHERE date_trunc('day',test_time) = date_trunc('day',now())
		UNION
		SELECT DISTINCT ON(A.test_subject_url) A.omf_tests_id id,A.test_time,A.test_subject_url,D.string return,C.name event_level,A.test_id FROM omf_tests A INNER JOIN events_info B ON (A.test_id = B.test_id) AND (A.return_code = B.return_code) INNER JOIN event_return_codes D ON A.return_code = D.code INNER JOIN event_levels C ON B.event_level = C.id WHERE date_trunc('day',test_time) = date_trunc('day',now())
		UNION
		SELECT DISTINCT ON(A.test_subject_url) A.ping_tests_id id,A.test_time,A.test_subject_url,D.string return,C.name event_level,A.test_id FROM ping_tests A INNER JOIN events_info B ON (A.test_id = B.test_id) AND (A.return_code = B.return_code) INNER JOIN event_return_codes D ON A.return_code = D.code INNER JOIN event_levels C ON B.event_level = C.id WHERE date_trunc('day',test_time) = date_trunc('day',now())

		"""
		#-------------------------------------------------------------------------------
		#SELECT FROM VIEW
		try:
			self._db_cur.execute("SELECT * FROM current_events;")
			self._db_connection.commit()
		
		except psycopg2.DatabaseError, e:
		
			if self._db_connection:
				self._db_connection.rollback()
		
			print 'Error %s' % e    
			#sys.exit(1)
		
		result = self._db_cur.fetchall()
		return result
	
	def fetch_island_locations(self):
		#-------------------------------------------------------------------------------
		#SELECT FROM VIEW
		try:
			self._db_cur.execute("SELECT * FROM island_locations;")
			self._db_connection.commit()
		
		except psycopg2.DatabaseError, e:
		
			if self._db_connection:
				self._db_connection.rollback()
		
			print 'Error %s' % e    
			#sys.exit(1)
		
		result = self._db_cur.fetchall()
		return result	
	
		
	def __del__(self):
		self._db_connection.close()



    
    



    




