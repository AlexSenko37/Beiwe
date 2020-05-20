#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
import sys

class ModAccel:

	"""
	The purpose of this class is to take the accelerometer table in Beiwe from having columns
	time_stamp   |        utc_time         | accuracy |         x          |         y          |         z          | patientid 
	and make a new derived table with just utc_time | mag | patientid
	"""

	def __init__(self, db = 'beiwe', user = 'postgres', password = 'secret'):

		self.db = db
		self.user = user
		self.password = password

	def deriveTable(self):

		con = None
		f = None

		try:

			con = psycopg2.connect(database = self.db, user = self.user, password = self.password)

			cur = con.cursor()

			drop_command = "DROP VIEW IF EXISTS accel_view"
			cur.execute(drop_command)

			command = "CREATE VIEW accel_view AS SELECT patientid, utc_time, date_trunc('hour', utc_time) AS utc_time_hr, date_trunc('day', utc_time) AS utc_time_day, (sqrt( x ^ 2.0 + y ^ 2.0 + z ^ 2.0) - 1) * 1000 AS MAG FROM accelerometer;"
			cur.execute(command)

			drop_command = "DROP TABLE IF EXISTS accel_mod"
			cur.execute(drop_command)

			command = "CREATE TABLE accel_mod AS SELECT * FROM accel_view"
			cur.execute(command)

			command = "ALTER TABLE accel_mod ALTER COLUMN mag SET DATA TYPE real;"
			cur.execute(command)

			con.commit()

		except psycopg2.DatabaseError as e:

			if con:
				con.rollback()

			print(f'Error {e}')
			sys.exit(1)

		except IOError as e:

			if con:
				con.rollback()

			print(f'Error {e}')
			sys.exit(1)

		finally:

			if con:
				con.close()

am = ModAccel()
am.deriveTable()



