#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
import sys
import glob
import re
import pandas as pd

class BeiweTable:

    def __init__(self, patient_ID, path, table_name, column_names, column_types, db = 'beiwe', user = 'postgres', password = 'secret'):

        self.db = db
        self.user = user
        self.password = password
        self.patient_ID = patient_ID
        self.path = path
        self.table_name = table_name
        self.column_names = column_names
        self.column_types = column_types

        con = None
        f = None

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

            if f:
                f.close()
    
    def build_create_query(self):
        create_command = f"CREATE TABLE {self.table_name}("
        for i,_ in enumerate(self.column_names):
            create_command += f"{self.column_names[i]} {self.column_types[i]}, "
        create_command = create_command[:-2] + ")"
        return create_command
        #CREATE TABLE pain(question_id varchar, question_type varchar, question_text varchar, question_answer_options varchar, answer int)"
    

    def __load__(self):

        con = None
        f = None

        # add .csv files in directory to table
        for file in glob.glob(self.path):

            try:

                con = psycopg2.connect(database = self.db, user = self.user, password = self.password)

                cur = con.cursor()

                f = open(file, 'r')
                next(f)
                cur.copy_from(f, self.table_name, sep=",")

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

                if f:
                    f.close()

class PainTable(BeiweTable):

    def __load__(self):

        con = None
        f = None

        # add .csv files in directory to table
        for file in glob.glob(self.path):

            try:

                df_pain_row = pd.read_csv(file, header = None, skiprows = [0])
                pain_score = df_pain_row.iloc[0][4]

                if pain_score != 'NO_ANSWER_SELECTED':

                    match = re.search(r'9ee\/(.*).csv', file)
                    time_stamp = match.group(1)
                    time_stamp = time_stamp.replace('_',':')

                    con = psycopg2.connect(database = self.db, user = self.user, password = self.password)

                    cur = con.cursor()

                    cur.execute(f"INSERT INTO {self.table_name}({self.column_names[0]}, {self.column_names[1]}, {self.column_names[2]}) VALUES('{time_stamp}', {pain_score}, '{self.patient_ID}')")

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

                if f:
                    f.close()


class AccelTable(BeiweTable):

    def __cleanup__(self):

        con = None
        f = None

        # add column to table with patient ID
        try:

            con = psycopg2.connect(database = self.db, user = self.user, password = self.password)

            cur = con.cursor()

            command = f"ALTER TABLE pain ADD COLUMN patientID varchar(10) DEFAULT '{self.patient_ID}';"
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


path = "~/3epwzqki/3epwzqki/survey_answers/56d60b801206f7036f8919ee/*.csv"
column_names = ['utc_time', 'pain_score','patientID']
column_types = ['timestamp', 'int', 'varchar']
ptable = PainTable(patient_ID = '3epwzqki', path = path, table_name = 'pain', column_names = column_names, column_types = column_types)
ptable.__load__()
#ptable.__cleanup__()

