import csv
import pandas as pd
import os
from os import listdir
from os.path import isfile, join
import numpy as np



auto_parsed_dir = input('Enter directory to auto parsed csv: ').strip() # 'development/in/parsed_csv/'
man_parsed_dir = input('Enter directory to manually parsed csv: ').strip() # 'development/in/counties/'
diff_dir = input('Input directory for differences files: ').strip() # 'development/in/csv_differences/'


auto_parsed_dir = auto_parsed_dir if auto_parsed_dir.endswith('/') else auto_parsed_dir+'/'
man_parsed_dir = man_parsed_dir if man_parsed_dir.endswith('/') else man_parsed_dir+'/'
diff_dir = diff_dir if diff_dir.endswith('/') else diff_dir+'/'

if not os.path.exists(diff_dir):
        os.mkdir(diff_dir)

#get all csv's parsed with the parser
csv_lst = [f for f in listdir(auto_parsed_dir) if (isfile(join(auto_parsed_dir, f)) and f.endswith('.csv'))]

'''get all the differences between the manually parsed csv's and the csv's done with the parser
#the manually parsed csv's and the parser parsed csv's have to have the same filename but exist
in different directories'''
for auto_parsed_csv in csv_lst:

        df_auto =  pd.read_csv(auto_parsed_dir + auto_parsed_csv)
        df_man = pd.read_csv(man_parsed_dir + auto_parsed_csv)

        #make sure they have the same column headers
        df_auto = df_auto[['county','precinct','office','district','party','candidate','votes']] 
        df_man = df_man[['county','precinct','office','district','party','candidate','votes']]

        #remove rows not created from parser.py
        df_man = df_man[df_man.office != 'Ballots Cast']
        df_man = df_man[df_man.office != 'Registered Voters']

        #make slight differences between the two csv's the same
        df_man['candidate'] = df_man['candidate'].str.replace('.','')
        df_auto['candidate'] = df_auto['candidate'].str.replace('.','')
        
        df_man['candidate'] = df_man['candidate'].str.strip()

        df_man['office'] = df_man['office'].str.strip()
        df_man['office'] = df_man['office'].str.replace('State Representative','State House')
        df_man['office'] = df_man['office'].str.replace('US House','U.S. House')
        df_man['office'] = df_man['office'].str.replace('Secretary of State','State Secretary')
        df_man['office'] = df_man['office'].str.replace('Auditor of State','State Auditor')
        df_man['office'] = df_man['office'].str.replace('Treasurer of State','State Treasurer')

        df_man['candidate'] = df_man['candidate'].str.lower()
        df_auto['candidate'] = df_auto['candidate'].str.lower()

        df_man['precinct'] = df_man['precinct'].str.lower()
        df_auto['precinct'] = df_auto['precinct'].str.lower()

        #get the differences in csv
        df = pd.concat([df_auto,df_man]).drop_duplicates(keep=False)
        df.sort_values(['precinct', 'office', 'district', 'party'], inplace=True)
        df.to_csv(diff_dir + auto_parsed_csv, index=False)
        perc_correct = str( 
                           round (
                                (len(df_man) + len(df_auto) - len(df))
                                /
                                (len(df_man)  + len(df_auto)) * 100
                           )
                        ) 
                           
        print( auto_parsed_csv + "," + str(len(df_auto)) + "," + perc_correct)
