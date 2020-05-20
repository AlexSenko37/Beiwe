#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Want to implement an algorithm that calculates the power spectral density and energy
of the accelerometer signal in 1 hour chunks.
Note that this means ignoring the 50% duty cycle of recording from the sensor- 
this may create artifacts. Hopefully they come out in the wash, but this is semething
to come back and consider.

Probably easier to match these 1 hour windows with pain scores later.
So go through whole accel_mod table and build a new hour-by-hour table
with fields energy, and the power spectral density for several (5?) frequency bands.
The hope is that the energy captures the activity level, and the power in different
frequency bands gives a sense of what activities were being done.
A major pitfall of that idea is that all human activities may fall into one (probably the 
lowest) frequency window. I suppose the harmonics might be different. But I may not want to use
exponentially-spaced bins to address that problem, with the spacing being the closest together
at low frequencies (such a relative widths of 1, 2, 4, 8, and 16).
'''
"""
Note: to attempt to increase speed, I increased the working memory (work_mem) in the configuration file
using this command to open the file: sudo -u postgres nano /Library/PostgreSQL/12/data/postgresql.conf
"""


import psycopg2
import sys
#import glob
#import re
import pandas as pd
import numpy as np
from scipy import signal
import time

class Hourly_FFT:

	def __init__(self, patient_ID, table_name, column_names, column_types, db = 'beiwe', user = 'postgres', password = 'secret'):

		self.db = db
		self.user = user
		self.password = password
		self.patient_ID = patient_ID
		#self.path = path
		self.table_name = table_name
		self.column_names = column_names
		self.column_types = column_types

		con = None
		f = None

		# initialize table
		try:

			con = psycopg2.connect(database = self.db, user = self.user, password = self.password)

			cur = con.cursor()

			drop_command = f"DROP TABLE IF EXISTS {self.table_name}"
			cur.execute(drop_command)
			
			create_command = self.build_create_query()

			cur.execute(create_command)

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
	
	def build_create_query(self):
		create_command = f"CREATE TABLE {self.table_name}("
		for i,_ in enumerate(self.column_names):
			create_command += f"{self.column_names[i]} {self.column_types[i]}, "
		create_command = create_command[:-2] + ")"
		return create_command
		#CREATE TABLE pain(question_id varchar, question_type varchar, question_text varchar, question_answer_options varchar, answer int)"
	

	def __load__(self):
		tic = time.time()
		# get list of days using distinct(utc_time_day) from table accel_mod
		try:

			con = psycopg2.connect(database = self.db, user = self.user, password = self.password)

			cur = con.cursor()

			command = f"SELECT distinct(utc_time_day) FROM accel_mod ORDER BY utc_time_day;"

			df_day_list = pd.read_sql_query(command, con)
			day_list = list(df_day_list['utc_time_day'])

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


		# for each day
		for day in day_list:

			# get a pandas dataframe with the accel data from that day

			try:

				con = psycopg2.connect(database = self.db, user = self.user, password = self.password)

				cur = con.cursor()

				command = f"SELECT utc_time, utc_time_hr, mag FROM accel_mod WHERE patientID = '{self.patient_ID}' and utc_time_day = '{day}' ORDER BY utc_time_day;"

				df_one_day = pd.read_sql_query(command, con)

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

			# get a list of distinct hours from the dataframe
			hours_list = list(df_one_day.utc_time_hr.unique())

			# initialize list that will contain rows to be writtent to the hourly_fft table
			fft_by_hour = []

			# for each hour
			for hour in hours_list:

				# get all ordered mag column from all accel_mod rows that match that hour
				# first get all matching rows from df_one_day
				df_hour = df_one_day.loc[df_one_day['utc_time_hr'] == hour]
				# then sort on utc_time
				df_hour = df_hour.sort_values(by=['utc_time'])
				# then get just the mag column as a list
				mag_vect = df_hour['mag'].tolist()

				hr_len = len(mag_vect)

				if hr_len >= 100:
					# get energy of signal
					hr_len = len(mag_vect)
					energy = np.sum(np.square(mag_vect)) / hr_len;

					# get power spectral density of signal
					nfft = hr_len // 11
					freqs, Pxx = signal.periodogram(mag_vect, fs = 10, nfft = nfft)

					# get average power in several frequency windows
					# due to the sampling frequency of 10 Hz, the FFT range is from 0 to 5 Hz
					# bins: 0-1, 1-2, 2-3, 3-4, 4-5
					df_power = pd.DataFrame()
					df_power['freqs'] = freqs
					df_power['Pxx'] = Pxx

					power1 = np.array(df_power[df_power['freqs'].between(0, 1)]['Pxx'])
					pow_len = len(power1)
					power1 = np.sum(power1) / pow_len

					power2 = np.array(df_power[df_power['freqs'].between(1, 2)]['Pxx'])
					pow_len = len(power2)
					power2 = np.sum(power2) / pow_len

					power3 = np.array(df_power[df_power['freqs'].between(2, 3)]['Pxx'])
					pow_len = len(power3)
					power3 = np.sum(power3) / pow_len

					power4 = np.array(df_power[df_power['freqs'].between(3, 4)]['Pxx'])
					pow_len = len(power4)
					power4 = np.sum(power4) / pow_len

					power5 = np.array(df_power[df_power['freqs'].between(4, 5)]['Pxx'])
					pow_len = len(power5)
					power5 = np.sum(power5) / pow_len

					this_hour = [self.patient_ID, hour, energy, power1, power2, power3, power4, power5]
					fft_by_hour.append(this_hour)

			# write to SQL table

			try:

				con = psycopg2.connect(database = self.db, user = self.user, password = self.password)

				cur = con.cursor()

				for hour in fft_by_hour:
					command = f"INSERT INTO hourly_fft({column_names[0]}, {column_names[1]}, {column_names[2]}, {column_names[3]}, {column_names[4]}, {column_names[5]}, {column_names[6]}, {column_names[7]}) VALUES('{self.patient_ID}', '{hour[1]}', {hour[2]}, {hour[3]}, {hour[4]}, {hour[5]}, {hour[6]}, {hour[6]})"
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
			
		toc = time.time()
		print(toc-tic)


#path = "~/3epwzqki/3epwzqki/survey_answers/56d60b801206f7036f8919ee/*.csv"
column_names = ['patientID', 'utc_time_hr', 'energy','power1', 'power2', 'power3','power4','power5']
column_types = ['varchar', 'timestamp', 'real', 'real', 'real', 'real', 'real', 'real']
fft_table = Hourly_FFT(patient_ID = '3epwzqki', table_name = 'hourly_fft', column_names = column_names, column_types = column_types)
fft_table.__load__()
#ptable.__cleanup__()