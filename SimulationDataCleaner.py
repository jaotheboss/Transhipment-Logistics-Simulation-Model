"""
[1/2] of the module that replaced `TuasShiftingSimulation.py`.
"""
import os
import pandas as pd
import datetime
import numpy as np

# Simulation Data Cleaner Class
class SimulationDataCleaner():
       """
       Description:  This class is meant to clean a particular raw data type into something more usable for the simulation.
       """
       def __init__(self, data):
              self.data = data
              
       def dt_converter(self, dt):
              """
              function:     converts a string into a datetime object
                            given that it follows the pattern of
                            '%d/%m/%Y %H:%M'
              input:        a string
              returns:      datetime object
              """
              result = datetime.datetime.strptime(dt, '%d/%m/%Y %H:%M')
              return result
       
       def scenarioA(self, df):
              """
              function:     transforming the data into values relevant to scenario A
                            ie. we take l_atb - d_atu
                            ### might change to l_atu - d_atu
              input:        dataframe
              returns:      array of connection time (n x 1)
              """
              l_atb = df.iloc[:, 6]
              d_atu = df.iloc[:, 5]
              ctime = l_atb - d_atu
              result = []
              for tdelta in ctime:
                     s = tdelta.total_seconds()
                     h = (s / 60) / 60
                     result.append(round(h, 2))
              result = np.asarray(result)
              return result
       
       def scenarioB(self, df):
              """
              function:     transforming the data into values relevant to scenario B
                            ie. we take l_atb - d_dt
              input:        dataframe
              returns:      array of connection time (n x 1)
              """
              l_atb = df.iloc[:, 6]
              d_dt = df.iloc[:, 4]
              ctime = l_atb - d_dt
              result = []
              for tdelta in ctime:
                     s = tdelta.total_seconds()
                     h = (s / 60) / 60
                     result.append(round(h, 2))
              result = np.asarray(result)
              return result
       
       def scenarioC(self, df):
              """
              function:     transforming the data into values relevant to scenario C
                            ie. we take l_dt - d_dt
              input:        dataframe
              returns:      array of connection time (n x 1)
              """
              l_dt = df.iloc[:, 7]
              d_dt = df.iloc[:, 4]
              ctime = l_dt - d_dt
              result = []
              for tdelta in ctime:
                     s = tdelta.total_seconds()
                     h = (s / 60) / 60
                     result.append(round(h, 2))
              result = np.asarray(result)
              return result
       
       def clean(self, export = False):
              """
              function:     cleans and organizes the data for simulation
              input:        dataframe
              returns:      cleaned dataset
              """
              # creating the connection time for each scenario
              scene_a = self.scenarioA(self.data)
              scene_b = self.scenarioB(self.data)
              scene_c = self.scenarioC(self.data)
       
              # collating all the data into one dataframe
              scene_df = pd.DataFrame(scene_a)
              scene_df.columns = ['a']
              scene_df['b'] = scene_b
              scene_df['c'] = scene_c
       
              # turns those with connection time <= 2 into 0
              scene_df = scene_df.where(lambda x: x > 2 , 0)
       
              # collating all the data into the original dataframe
              self.data['Connect_SceneA'] = scene_df['a']
              self.data['Connect_SceneB'] = scene_df['b']
              self.data['Connect_SceneC'] = scene_df['c']
       
              # adding in the sorting variable (the time difference)
              time_data = self.data.iloc[:, [4, 5, 8]]
              ## let ld_A = L_ATU - D_ATU
              ld_A = time_data.iloc[:, 2] - time_data.iloc[:, 1]
              ld_A = list(map(lambda x: x.total_seconds(), ld_A))
              ## let ld_D = L_ATU - D_DT
              ld_D = time_data.iloc[:, 2] - time_data.iloc[:, 0]
              ld_D = list(map(lambda x: x.total_seconds(), ld_D))
       
              # collating all the data into the original dataframe
              self.data['ld_A'] = ld_A
              self.data['ld_D'] = ld_D
       
              # remove nan's
              self.data = self.data.loc[np.isnan(self.data['LEN_Q']) == False, :]
       
              if export:
                     self.data.to_excel(os.getcwd() + '\\new_data.xlsx', index = False)
       
              return self.data
       
       def extract_scene_data(self, scenario, df = None):
              """
              function:     extracts, filters and organises the dataset to retrieve
                            the dataset of a particular scenario
              input:        cleaned dataset; a dataframe
                            *data has to be cleaned with this file's `clean` function
              returns:      dataset for a particular scenario
              """
              if df == None:
                     df = self.data
              # retrieve the scenario that's been requested to be extracted
              if scenario == 'a':
                     # only extracting variables for scenario A
                     scene_a_data = df.iloc[:, [0, 1, 4, 9]]
                     # filter away those that have a connection time of <= 2 hours
                     scene_a_data = scene_a_data.loc[scene_a_data.Connect_SceneA != 0,:]
       
                     # sort, neaten up and return
                     scene_a_data = scene_a_data.sort_values(['DISC_DT'])
                     scene_a_data = scene_a_data.reset_index()
                     self.data = scene_a_data
                     return scene_a_data
       
              elif scenario == 'b':
                     # only extracting variables for scenario B
                     scene_b_data = df.iloc[:, [0, 1, 4, 10]]
                     # filter away those that have a connection time of <= 2 hours
                     scene_b_data = scene_b_data.loc[scene_b_data.Connect_SceneB != 0,:]
       
                     # sort, neaten up and return
                     scene_b_data = scene_b_data.sort_values(['DISC_DT'])
                     scene_b_data = scene_b_data.reset_index()
                     self.data = scene_b_data
                     return scene_b_data
       
              else:
                     # only extracting variables for scenario C
                     scene_c_data = df.iloc[:, [0, 1, 4, 11]]
                     # filter away those that have a connection time of <= 2 hours
                     scene_c_data = scene_c_data.loc[scene_c_data.Connect_SceneC != 0,:]
       
                     # sort, neaten up and return
                     scene_c_data = scene_c_data.sort_values(['DISC_DT'])
                     scene_c_data = scene_c_data.reset_index()
                     self.data = scene_c_data
                     return scene_c_data
              
       def fill_fake_events(self):
              """
              function:     to fill the DISC_DT of the dataframe with fake event intervals
              input:        DataFrame with a DISC_DT variable
              output:       DataFrame that includes fake observations 
              """
              df = self.data
              result = df.copy()
              disc_dt = result.loc[:, 'DISC_DT']
              for i in range(1, len(disc_dt)):
                     if i % 1000 == 0:
                            print(i)
                     end, start = disc_dt[i], disc_dt[i - 1]
                     diff = (end - start).seconds
                     if diff >= 3600: # 30 minutes
                            period = pd.period_range(start + datetime.timedelta(minutes = 1), end - datetime.timedelta(minutes = 1), freq = '5T').to_timestamp()
                            for dt in period:
                                   result = result.append(pd.DataFrame([[-1, 'Neither', -1, -1, None, dt, None, None, None, None, -1, -1]], columns = result.columns))
              result.to_csv('result_with_fake_events.csv')
              return result
