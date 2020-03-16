"""
This .py file is to be read as a module
"""
import os
import pandas as pd
import datetime
import numpy as np
from itertools import compress
import matplotlib.pyplot as plt
from math import floor

data = pd.read_excel('DATA_20200109_sent.xlsx')

def dt_converter(dt):
       """
       function:     converts a string into a datetime object
                     given that it follows the pattern of
                     '%d/%m/%Y %H:%M'
       input:        a string
       returns:      datetime object
       """
       result = datetime.datetime.strptime(dt, '%d/%m/%Y %H:%M')
       return result

def scenarioA(df):
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

def scenarioB(df):
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

def scenarioC(df):
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

def clean_data(df):
       """
       function:     cleans and organizes the data for simulation
       input:        dataframe
       returns:      cleaned dataset
       """
       # creating the connection time for each scenario
       scene_a = scenarioA(df)
       scene_b = scenarioB(df)
       scene_c = scenarioC(df)

       # collating all the data into one dataframe
       scene_df = pd.DataFrame(scene_a)
       scene_df.columns = ['a']
       scene_df['b'] = scene_b
       scene_df['c'] = scene_c

       # turns those with connection time <= 2 into 0
       scene_df = scene_df.where(lambda x: x > 2 , 0)

       # collating all the data into the original dataframe
       df['Connect_SceneA'] = scene_df['a']
       df['Connect_SceneB'] = scene_df['b']
       df['Connect_SceneC'] = scene_df['c']

       # adding in the sorting variable (the time difference)
       time_data = df.iloc[:, [4, 5, 8]]
       ## let ld_A = L_ATU - D_ATU
       ld_A = time_data.iloc[:, 2] - time_data.iloc[:, 1]
       ld_A = list(map(lambda x: x.total_seconds(), ld_A))
       ## let ld_D = L_ATU - D_DT
       ld_D = time_data.iloc[:, 2] - time_data.iloc[:, 0]
       ld_D = list(map(lambda x: x.total_seconds(), ld_D))

       # collating all the data into the original dataframe
       df['ld_A'] = ld_A
       df['ld_D'] = ld_D

       # remove nan's
       df = df.loc[np.isnan(df['LEN_Q']) == False, :]

       export = eval(input('Would you like to export the new data? [True/False]: '))
       if export:
              df.to_excel(os.getcwd() + '\\new_data.xlsx', index = False)

       return df

def extract_scene_data(df, scenario):
       """
       function:     extracts, filters and organises the dataset to retrieve
                     the dataset of a particular scenario
       input:        cleaned dataset; a dataframe
                     *data has to be cleaned with this file's `clean` function
       returns:      dataset for a particular scenario
       """
       # retrieve the scenario that's been requested to be extracted
       # scenario = input('Which scenario data would you like extracted? [a, b, c]: ')

       if scenario == 'a':
              # only extracting variables for scenario A
              scene_a_data = df.iloc[:, [0, 1, 4, 9]]
              # filter away those that have a connection time of <= 2 hours
              scene_a_data = scene_a_data.loc[scene_a_data.Connect_SceneA != 0,:]

              # sort, neaten up and return
              scene_a_data = scene_a_data.sort_values(['DISC_DT'])
              scene_a_data = scene_a_data.reset_index()
              return scene_a_data

       elif scenario == 'b':
              # only extracting variables for scenario B
              scene_b_data = df.iloc[:, [0, 1, 4, 10]]
              # filter away those that have a connection time of <= 2 hours
              scene_b_data = scene_b_data.loc[scene_b_data.Connect_SceneB != 0,:]

              # sort, neaten up and return
              scene_b_data = scene_b_data.sort_values(['DISC_DT'])
              scene_b_data = scene_b_data.reset_index()
              return scene_b_data

       else:
              # only extracting variables for scenario C
              scene_c_data = df.iloc[:, [0, 1, 4, 11]]
              # filter away those that have a connection time of <= 2 hours
              scene_c_data = scene_c_data.loc[scene_c_data.Connect_SceneC != 0,:]

              # sort, neaten up and return
              scene_c_data = scene_c_data.sort_values(['DISC_DT'])
              scene_c_data = scene_c_data.reset_index()
              return scene_c_data
       
def fill_fake_events(df):
       """
       function:     to fill the DISC_DT of the dataframe with fake event intervals
       input:        DataFrame with a DISC_DT variable
       output:       DataFrame that includes fake observations 
       """
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

####################
# PM Class
class PM():
       def __init__(self, index, starting_location, working_hours, work_shift):
              self.index = index
              self.origin = starting_location
              self.location = starting_location
              self.current_dest = None
              self.trips_count = {'full': 0, # trip count for type
                                  'half': 0,
                                  'empty': 0,
                                  'dest': []}# trip count for destination
              self.working_hours = working_hours
              self.work_shift = work_shift
              self.work_log = {'depart': [], # to track when it departs for transport
                               'arrive': [], # and when it arrives at location
                               'container': []} # to track which PM took which container

       def set_working_hours(self, hours):
              """
              function:     set the working hours for the PM vehicle
              input:        a list of the hours (out of 24 hours) that the PM will be working for
              output:       None. Will update the working hours of the PM
              """
              # hours_working = sum(hours)
              self.working_hours = hours
              # print('Total hours worked:', hours_working)

       def set_work_shift(self, shift):
              """
              function:     set the work shift of this particular PM
              input:        which shift the PM is working
              output:       None. But will update the work shift
              """
              self.work_shift = shift

       def able_to_work(self, time):
              """
              function:     check if the PM is available to make a delivery
              input:        a timing; datetime value
              output:       boolean
              """
              current_hour = time.time().hour
              current_minute = time.time().minute
              if current_minute < 30:
                     current_hour -= 1
                     if current_hour == -1:
                            current_hour = 23
              # current_minute = time.time().minute
              # current_second = time.time().second
              # 0 represents 12:30am to 1:30am, 23 represents 11:30pm to 12:30am

              # flexi
              work_shift_meal_times = {'7m': {'0': 11, '1': 12},
                                       '7n': {'0': 1, '1': 2},
                                       '8m': 11,
                                       '8n': 1,
                                       '9m': 12,
                                       '9n': 2}
              meal_shift_d = str(np.random.randint(0, 2))
              work_shift_meal_times['7m'], work_shift_meal_times['7n'] = work_shift_meal_times['7m'][meal_shift_d], work_shift_meal_times['7n'][meal_shift_d]

              # make sure there's a 2 hour gap before they panggang
              if self.working_hours[current_hour] == 1 and self.working_hours[(current_hour + 1) % 24] == 1 and self.working_hours[(current_hour + 2) % 24] == 1:
                     # 1 hour gap before they go off for lunch
                     if current_hour != work_shift_meal_times[self.work_shift] and self.working_hours[(work_shift_meal_times[self.work_shift] + 1) % 24] == 1:
                            return True
              # have to add in their meal timings
              return False

       def reset_tracking(self):
              self.trips_count = {'full': 0,
                                  'half': 0,
                                  'empty': 0,
                                  'dest': []}
              self.work_log = {'depart': [],
                               'arrive': [],
                               'container': []}

       def reset_working_hours(self):
              work_shifts = {'7m': [0]*7 + [1]*12 + [0]*5,
                             '7n': [1]*7 + [0]*12 + [1]*5,
                             '8m': [0]*8 + [1]*12 + [0]*4,
                             '8n': [1]*8 + [0]*12 + [1]*4,
                             '9m': [0]*9 + [1]*12 + [0]*3,
                             '9n': [1]*9 + [0]*12 + [1]*3}

              self.working_hours = work_shifts[self.work_shift]

       def reset_location(self):
              self.location = self.origin
              self.current_dest = None

       def empty_movement(self):
              """
              function:     to get the statistics of all the empty trips made by this PM
              input:        nothing
              output:       stats on empty trips
              """
              empty_trip_index = [i for i, v in enumerate(self.work_log['container']) if v == 'empty']
              duration_out = 0
              count = len(empty_trip_index)
              print('Count:', count)
              print('\nTime Stamps of Empty Movement:')
              for i in empty_trip_index:
                     duration_out += (self.work_log['arrive'][i] - self.work_log['depart'][i]).total_seconds()
                     print([self.work_log['depart'][i], self.work_log['arrive'][i]])
              print('\nDuration of Empty Movement:\n')
              print(duration_out, 'seconds')


       def idle_timings(self):
              """
              function:     collates together the timings of which this PM has been idle for
              input:        nothing
              output:       idle timings
              """
              idle_timings = []
              if len(self.work_log['arrive']) == 0:
                     if len(self.work_log['depart']) == 0:
                            return None
                     else:
                            idle_timings.append([datetime.datetime(self.work_log['depart'][0].date().year, 
                                                      self.work_log['depart'][0].date().month, 
                                                      self.work_log['depart'][0].date().day, 
                                                      7, 
                                                      30, 
                                                      00), self.work_log['depart'][0]])
                            return idle_timings
              
              a = self.work_log['arrive'].copy()
              d = self.work_log['depart'].copy()

              curr_day = datetime.datetime(d[0].year, d[0].month, d[0].day)
              last_day = datetime.datetime(a[-1].year, a[-1].month, a[-1].day)
              
              days_log = []
              
              if self.work_shift[1] == 'm':
                     while (last_day - curr_day).days >= 0:
                            # clean_a = list(filter(lambda x: (x.year == curr_day.year and x.month == curr_day.month and x.day == curr_day.day), a))
                            clean_a = [x for x in a if (x.year == curr_day.year and x.month == curr_day.month and x.day == curr_day.day)]
                            # clean_d = list(filter(lambda x: (x.year == curr_day.year and x.month == curr_day.month and x.day == curr_day.day), d))
                            clean_d = [x for x in d if (x.year == curr_day.year and x.month == curr_day.month and x.day == curr_day.day)]
                            
                            day_log = {'depart': clean_d + [datetime.datetime(curr_day.year, curr_day.month, curr_day.day, int(self.work_shift[0]) + 12, 30, 0)], 
                                       'arrive': [datetime.datetime(curr_day.year, curr_day.month, curr_day.day, int(self.work_shift[0]), 30, 0)] + clean_a}
                            
                            days_log.append(day_log)
                            curr_day += datetime.timedelta(days = 1)
              else:
                     if a[-1].hour >= 19:
                            last_day += datetime.timedelta(days = 1)
                     while (last_day - curr_day).days > 0:
                            clean_a = [x for x in a if (x.year == last_day.year and x.month == last_day.month and x.day == last_day.day and x.hour < int(self.work_shift[0])) or (x.year == last_day.year and x.month == last_day.month and x.day == last_day.day and x.hour == int(self.work_shift[0]) and x.minute <= 30)]
                            
                            clean_d = [x for x in d if (x.year == last_day.year and x.month == last_day.month and x.day == last_day.day and x.hour < int(self.work_shift[0])) or (x.year == last_day.year and x.month == last_day.month and x.day == last_day.day and x.hour == int(self.work_shift[0]) and x.minute <= 30)]
                            clean_d += [datetime.datetime(last_day.year, last_day.month, last_day.day, int(self.work_shift[0]), 30, 0)]
                            
                            last_day -= datetime.timedelta(days = 1)
                            
                            clean_a = [x for x in a if (x.year == last_day.year and x.month == last_day.month and x.day == last_day.day and x.hour > int(self.work_shift[0]) + 12) or (x.year == last_day.year and x.month == last_day.month and x.day == last_day.day and x.hour == int(self.work_shift[0]) + 12 and x.minute >= 30)] + clean_a
                         
                            clean_d = [x for x in d if (x.year == last_day.year and x.month == last_day.month and x.day == last_day.day and x.hour > int(self.work_shift[0]) + 12) or (x.year == last_day.year and x.month == last_day.month and x.day == last_day.day and x.hour == int(self.work_shift[0]) + 12 and x.minute >= 30)] + clean_d
                            clean_a = [datetime.datetime(last_day.year, last_day.month, last_day.day, int(self.work_shift[0]) + 12, 30, 0)] + clean_a
                            
                            day_log = {'depart': clean_d, 
                                       'arrive': clean_a}
                            
                            days_log.append(day_log)
              total_duration = 0
              print('\nTime Stamps of Idle Time:')
              for i in days_log:
                     n = len(i['arrive'])
                     for j in range(n):
                            duration = get_hours(i['depart'][j] - i['arrive'][j])
                            total_duration += duration
                            if duration <= 0:
                                   continue
                            print('From:', i['arrive'][j], '\t', 'To:', i['depart'][j], '\tDuration:', duration)
                     if len(i['depart']) != n:
                            end = (get_hours(i['depart'][-1] - i['depart'][-2]) - 2)
                            total_duration += end
              print('\nTotal Duration:', round(total_duration, 2), '\n')
              return days_log

       def retrieve_container_indexes(self):
              """
              function:     returns a flattened list of the container indexes (wrt to the dataframe)
              input:        nothing
              output:       a list of indexes
              """
              return [x for x in flatten(self.work_log['container']) if type(x) != str] # list(filter(lambda x: type(x) != str, flatten(self.work_log['container'])))

       def retrieve_on_road_timings(self):
              """
              function:     to obtain solely the timings that the PM is on the road. excluding the
                            offload, mounting and transit within the terminal timings
              input:        nothing
              output:       start and end time on the road
              """
              depart = [i + datetime.timedelta(minutes = 15) for i in self.work_log['depart']] # because 0.25 hours spent on mounting
              arrive = [i - datetime.timedelta(minutes = 15) for i in self.work_log['arrive']] # because 0.25 hours spent on offload
              if len(depart) == len(arrive):
                     for i in range(len(arrive)):
                            print('Depart:', depart[i], '\tArrive:', arrive[i])
              else:
                     for i in range(len(arrive)):
                            print('Depart:', depart[i], '\tArrive:', arrive[i])
                     print('Depart:', depart[-1], '\tArrive:', 'Transit')

       def work_time_portfolio(self, show = True):
              """
              function:     to calculate the represent the distribution of work and
                            non-work timings for this PM
              input:        None
              output:       graphic of work portfolio
              """
              days_log = self.idle_timings()
              if days_log == None:
                     return [0, 0, 0, 0, 0]
              total_idle = 0
              n_arrive = 0
              n_depart = 0
              for i in days_log:
                     n = len(i['arrive'])
                     m = len(i['depart'])
                     
                     n_arrive += (n - 1)
                     n_depart += (m - 1)
              
                     for j in range(n):
                            duration = get_hours(i['depart'][j] - i['arrive'][j])
                            total_idle += duration
                            if duration <= 0:
                                   continue
                     if m != n:
                            total_idle += (get_hours(i['depart'][-1] - i['depart'][-2]) - 2)
                            
              n = len(days_log)
              total_time = n*12
              total_meal_time = n*1
              total_idle -= total_meal_time
              total_active = total_time - total_idle
              total_mount_time, total_offload_time = 0.25*n_depart, 0.25*n_arrive
              total_on_road = total_active - total_mount_time - total_offload_time
              
              if show:
                     plt.pie([total_idle, total_meal_time, total_on_road, total_mount_time, total_offload_time],
                             labels = ['idle', 'meals', 'on road', 'mount', 'offload'],
                             labeldistance = 1,
                             autopct = '%1.1f%%',
                             explode = [0.1, 0.1, 0, 0, 0],
                             startangle = 90)
                     print('For PM_' + str(self.index))
                     print('\nTime Spent on:\n')
                     print('Idle:\t\t\t', round(total_idle, 2), 'hours', 
                           '\nMeals:\t\t\t', total_meal_time, 'hours', 
                           '\nOn Road:\t\t', round(total_on_road, 2), 'hours',  
                           '\nMounting/Offload:\t', total_mount_time + total_offload_time, 'hours')
              return [total_idle, total_meal_time, total_on_road, total_mount_time, total_offload_time]


# how many vehicles at each location at the start
tuas_vehicles = 150
city_vehicles = 150

# at what thresholds should we start prioritising sending the container over
threshold_connectingtime = 12
threshold_back_log = 58
threshold_dd = 55
threshold_dd_empty = 75
threshold_transit_to_dest = 0.2

# how many hours forward should we look for the demand
forward_dd = 2

# at what quantity of vehicles should we start sending over empty PMs
threshold_vehicle_half = 25 # if the other side has this many or below, it'll send half PMs

# tracking of Prime Movers as a whole
PMs_track = {'tuas': tuas_vehicles,         # stands for Prime Movers
       'city': city_vehicles,
       'transit': {'dest': [], 'time' : [], 'index': [], 'size': []}
       }

# tracking containers
              
container = {'moved_index': [],
             'time': {'depart': [], 'arrive': []},
             'excess': []
             }

# to track the progression of the amount of PMs at each location
# for plotting; debugging
transit_track = []
tuas_track = []
city_track = []
back_log_track_city = []
back_log_track_tuas = []
dd_track_city = []
dd_track_tuas = []

transit_track_append = transit_track.append
tuas_track_append = tuas_track.append
city_track_append = city_track.append
back_log_track_city_append = back_log_track_city.append
back_log_track_tuas_append = back_log_track_tuas.append
dd_track_city_append = dd_track_city.append
dd_track_tuas_append = dd_track_tuas.append

# track how many full, half or empty vehicles that have been pushed off
full_load = [0]
half_load = [0]
empty_load = [0]

# how many PMs to move over, when either side is low in PMs
move_over = 1

# Initialize PMs
PMs = {}
for i in range(1, 301):
       if i <= 150:
              if i <= 25:
                     PMs['PM_' + str(i)] = PM(i, 'city', [0]*7 + [1]*12 + [0]*5, '7m')
              elif i <= 50:
                     PMs['PM_' + str(i)] = PM(i, 'city', [1]*7 + [0]*12 + [1]*5, '7n')
              elif i <= 75:
                     PMs['PM_' + str(i)] = PM(i, 'city', [0]*8 + [1]*12 + [0]*4, '8m')
              elif i <= 100:
                     PMs['PM_' + str(i)] = PM(i, 'city', [1]*8 + [0]*12 + [1]*4, '8n')
              elif i <= 125:
                     PMs['PM_' + str(i)] = PM(i, 'city', [0]*9 + [1]*12 + [0]*3, '9m')
              else:
                     PMs['PM_' + str(i)] = PM(i, 'city', [1]*9 + [0]*12 + [1]*3, '9n')
       else:
              if i <= 175:
                     PMs['PM_' + str(i)] = PM(i, 'tuas', [0]*7 + [1]*12 + [0]*5, '7m')
              elif i <= 200:
                     PMs['PM_' + str(i)] = PM(i, 'tuas', [1]*7 + [0]*12 + [1]*5, '7n')
              elif i <= 225:
                     PMs['PM_' + str(i)] = PM(i, 'tuas', [0]*8 + [1]*12 + [0]*4, '8m')
              elif i <= 250:
                     PMs['PM_' + str(i)] = PM(i, 'tuas', [1]*8 + [0]*12 + [1]*4, '8n')
              elif i <= 275:
                     PMs['PM_' + str(i)] = PM(i, 'tuas', [0]*9 + [1]*12 + [0]*3, '9m')
              else:
                     PMs['PM_' + str(i)] = PM(i, 'tuas', [1]*9 + [0]*12 + [1]*3, '9n')

############## HELPER FUNCTIONS FOR THE SIMULATION ################
def flatten(container):
       """
       function:     to flatten a nested list into a list
       input:        list
       output:       flatten object. return as list(flatten(input))
       """
       for i in container:
              if isinstance(i, (list,tuple)):
                     for j in flatten(i):
                            yield j
              else:
                     yield i

def container_info(data, container_id, info):
       """
       function:     to extract data out of the dataframe based on the container id
       input:        data, the container id and the information that we want extracted
       output:       info that we wanted extracted
       """
       if info == 'size':
              if container_id == 'empty':
                     return 'empty'
              elif data.loc[data['index'] == container_id, 'LEN_Q'].iloc[0] <= 22: # can use data.loc[data['index'] == container_id, 'LEN_Q'].item()
                     return 'half'
              else:
                     return 'full'
       return None

def get_transit_dest_count(pms):
       """
       function:     counts the number of PMs that are currently on their way to a particular location
       input:        dictionary of PMs
       output:       the count of PMs that are on their way over to Tuas or City
       """
       list_of_PMs = list(pms.values())
       list_of_PMs = list(filter(lambda x: x.location == 'transit', list_of_PMs))
       city = list(map(lambda x: x.current_dest, list_of_PMs)).count('city')
       tuas = list(map(lambda x: x.current_dest, list_of_PMs)).count('tuas')
       return {'city': city, 'tuas': tuas}

def get_hours(timedelta):
       """
       function:     to convert a timedelta object into hours
       input:        timedelta object
       returns:      time in terms of hours
       """
       result = timedelta.total_seconds()
       result = (result / 60) / 60
       result = round(result, 2)
       return result

def reset_variables():
       """
       function:     to reset the variables
       input:        None
       returns:      None
       """
       global tuas_vehicles
       global city_vehicles

       global threshold_connectingtime
       global threshold_back_log
       global threshold_dd
       global threshold_dd_empty
       global threshold_transit_to_dest

       global forward_dd

       global threshold_vehicle_half

       global PMs_track

       global container

       global transit_track
       global tuas_track
       global city_track
       global back_log_track_city
       global back_log_track_tuas
       global dd_track_city
       global dd_track_tuas

       global full_load
       global half_load
       global empty_load

       global move_over


       # how many vehicles at each location at the start
       tuas_vehicles = 150
       city_vehicles = 150

       # at what thresholds should we start prioritising sending the container over
       threshold_connectingtime = 12 # original 12
       threshold_back_log = 58 # original 58
       threshold_dd = 55 # original 55
       threshold_dd_empty = 75
       threshold_transit_to_dest = 0.2

       # how many hours forward should we look for the demand
       forward_dd = 2

       # at what quantity of vehicles should we start sending over empty PMs
       threshold_vehicle_half = 25 # if the other side has this many or below, it'll send half PMs

       # tracking of Prime Movers as a whole
       PMs_track = {'tuas': tuas_vehicles,         # stands for Prime Movers
                    'city': city_vehicles,
                    'transit': {'dest': [], 'time' : [], 'index': [], 'size': []}
                    }

       # tracking containers
       container = {'moved_index': [],
                    'time': {'depart': [], 'arrive': []},
                    'excess': []
                    }


       # to track the progression of the amount of PMs at each location
       # for plotting; debugging
       transit_track = []
       tuas_track = []
       city_track = []
       back_log_track_city = []
       back_log_track_tuas = []
       dd_track_city = []
       dd_track_tuas = []

       # track how many full, half or empty vehicles that have been pushed off
       full_load = [0]
       half_load = [0]
       empty_load = [0]

       # how many PMs to move over, when either side is low in PMs
       move_over = 1

       # Initialize PMs
       for pm in PMs.values():
              pm.reset_tracking()
              pm.reset_working_hours()
              pm.reset_location()

def change_variable(value, name):
       """
       function:     to change the value of a variable
       input:        value and name of variable
       returns:      None
       """
       global tuas_vehicles
       global city_vehicles
       global threshold_connectingtime
       global threshold_back_log
       global threshold_dd
       global threshold_vehicle_half
       global threshold_dd_empty
       global PMs_track
       global move_over
       global container
       global forward_dd
       global threshold_transit_to_dest

       if name == 'tuas_vehicles':
              tuas_vehicles = value
       elif name == 'city_vehicles':
              city_vehicles = value
       elif name == 'threshold_connectingtime':
              threshold_connectingtime = value
       elif name == 'threshold_back_log':
              threshold_back_log = value
       elif name == 'threshold_dd':
              threshold_dd = value
       elif name == 'threshold_vehicle_half':
              threshold_vehicle_half = value
       elif name == 'threshold_dd_empty':
              threshold_dd_empty = value
       elif name == 'move_over':
              move_over = value
       elif name == 'forward_dd':
              forward_dd = value
       elif name == 'threshold_transit_to_dest':
              threshold_transit_to_dest = value
       PMs_track = {'tuas': tuas_vehicles,         # stands for Prime Movers
              'city': city_vehicles,
              'transit': {'dest': [], 'time' : [], 'index': [], 'size': []}
              }
       container = {'moved_index': [],
             'time': {'depart': [], 'arrive': []},
             'excess': []
             }
       PMs = {}
       for i in range(1, 301):
              if i <= 150:
                     if i <= 25:
                            PMs['PM_' + str(i)] = PM(i, 'city', [0]*7 + [1]*12 + [0]*5, '7m')
                     elif i <= 50:
                            PMs['PM_' + str(i)] = PM(i, 'city', [1]*7 + [0]*12 + [1]*5, '7n')
                     elif i <= 75:
                            PMs['PM_' + str(i)] = PM(i, 'city', [0]*8 + [1]*12 + [0]*4, '8m')
                     elif i <= 100:
                            PMs['PM_' + str(i)] = PM(i, 'city', [1]*8 + [0]*12 + [1]*4, '8n')
                     elif i <= 125:
                            PMs['PM_' + str(i)] = PM(i, 'city', [0]*9 + [1]*12 + [0]*3, '9m')
                     else:
                            PMs['PM_' + str(i)] = PM(i, 'city', [1]*9 + [0]*12 + [1]*3, '9n')
              else:
                     if i <= 175:
                            PMs['PM_' + str(i)] = PM(i, 'tuas', [0]*7 + [1]*12 + [0]*5, '7m')
                     elif i <= 200:
                            PMs['PM_' + str(i)] = PM(i, 'tuas', [1]*7 + [0]*12 + [1]*5, '7n')
                     elif i <= 225:
                            PMs['PM_' + str(i)] = PM(i, 'tuas', [0]*8 + [1]*12 + [0]*4, '8m')
                     elif i <= 250:
                            PMs['PM_' + str(i)] = PM(i, 'tuas', [1]*8 + [0]*12 + [1]*4, '8n')
                     elif i <= 275:
                            PMs['PM_' + str(i)] = PM(i, 'tuas', [0]*9 + [1]*12 + [0]*3, '9m')
                     else:
                            PMs['PM_' + str(i)] = PM(i, 'tuas', [1]*9 + [0]*12 + [1]*3, '9n')

def PM_locations():
       """
       function:     get the locations of all the PMs
       input:        None
       returns:      a string that states the location of all the PMs
       """
       n_transit = len(PMs_track['transit']['time'])
       n_city = PMs_track['city']
       n_tuas = PMs_track['tuas']
       print('Transit:', n_transit, 'City:', n_city, 'Tuas:', n_tuas)

def check_pm_avail(time, dest, trip_type):
       """
       function:     get an available PM to do a transfer
       input:        timing, destination, type of trip (full, half, empty)
       output:       either the id of an available PM or False
       """
       ds = {'city': 'tuas', 'tuas': 'city'}
       list_of_PMs = [x for x in PMs.values() if (x.able_to_work(time) and x.location == ds[dest])]

       if list_of_PMs:
              least = -1
              p = False
              for pm in list_of_PMs:
                     l = len(pm.work_log['depart'])
                     if l == 0:
                            return pm
                     elif l < least or least == -1:
                            least = l
                            p = pm
              return p
       return False

def pm_arrival_updater(duration_out, size, timing):
       """
       function:     updates whether the pm has arrived at the location
                     the twist being, the timing will be dynamic based on
                     the size of the container being moved, and whether
                     or not its peak hour
       input:        how long the pm has been out, the sizes of container
                     each pm is transporting and the discharge times of
                     each pm
       output:       a boolean list representing those that have reached
                     vs. those that haven't
       """
       def boolean_generator(index):
              t = timing[index].time().hour
              do = duration_out[index]
              s = size[index]
              if (t >= 7 and t <= 9) or (t >= 17 and t <= 20):
                     if s == 'full':
                            # this timing would include the mounting time at PP/Tuas
                            # and the offload time at PP/Tuas
                            if do > (2.5 + 0.25 + 0.25):
                                   return False
                            else:
                                   return True
                     elif s == 'half':
                            # this timing would include the mounting time at PP/Tuas
                            # and the offload time at PP/Tuas
                            if do > (2.3 + 0.25 + 0.25):
                                   return False
                            else:
                                   return True
                     else:
                            # only the travel time
                            if do > (2 + 0.25 + 0.25):
                                   return False
                            else:
                                   return True
              else:
                     if s == 'full':
                            # this timing would include the mounting time at PP/Tuas
                            # and the offload time at PP/Tuas
                            if do > (2 + 0.25 + 0.25):
                                   return False
                            else:
                                   return True
                     elif s == 'half':
                            # this timing would include the mounting time at PP/Tuas
                            # and the offload time at PP/Tuas
                            if do > (1.8 + 0.25 + 0.25):
                                   return False
                            else:
                                   return True
                     else:
                            # this is only travel time
                            if do > (1.5 + 0.25 + 0.25):
                                   return False
                            else:
                                   return True
       result = list(map(boolean_generator, range(len(duration_out))))
       result = np.array(result)
       return result

def travel_duration(size, timing):
       """
       function:     to determine the travel duration of a particular PM based on the time of travel and the
                     size of container that's being transported
       input:        size of container and discharge time
       output:       travel duration

       """
       if (timing.time().hour >= 7 and timing.time().hour <= 9) or (timing.time().hour >= 17 and timing.time().hour <= 20):
              if size == 'full':
                     return 3
              elif size == 'half':
                     return 2.8
              else:
                     return 2.5
       else:
              if size == 'full':
                     return 2.5
              elif size == 'half':
                     return 2.3
              else:
                     return 2

def shift_change_analysis(shift):
       pms = PMs.values()
       pms = np.array(filter(lambda x: x.work_shift == shift, pms))
       end_shift_pm_locations = []
       for pm in pms:
              time_stamps = pm.work_log['arrive']
              if not time_stamps:
                     continue
              start_date = time_stamps[0].date()
              end_shift_timings = []
              for i in range(len(time_stamps) - 1):
                     if shift[1] == 'm':
                            if time_stamps[i + 1] != start_date:
                                   end_shift_timings.append(i)
                     else:
                            if time_stamps[i + 1] != start_date:
                                   end_shift_timings.append(i + 1)
                     start_date += datetime.timedelta(days = 1)
              end_shift_locations = [e for i, e in enumerate(pm.trips_count['dest']) if i in end_shift_timings]
              if len(pm.work_log['arrive']) != len(pm.work_log['depart']):
                     end_shift_locations.append(pm.current_dest)
              end_shift_pm_locations.append(end_shift_locations)
       tuas = 0
       city = 0
       # at this point, end_shift_pm_locations = [['city', 'tuas', ...], [...], [...], ...], each element is a list of all the locations a particular pm was at by the end of the shift
       for i in end_shift_pm_locations:
              tuas += i.count('tuas')
              city += i.count('city')
       print('Average Location of PMs during Change Shift for:', 'Morning Shift' if shift[1] == 'm' else 'Night Shift', str(shift[0]) + ':30' + ('am' if shift[1] == 'm' else 'pm'), 'to', str(shift[0]) + ':30' + ('pm\n' if shift[1] == 'm' else 'am\n'))
       def make_autopct(values):
              def my_autopct(pct):
                     total = sum(values)
                     val = int(round(pct*total/100.0))
                     return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
              return my_autopct
       plt.pie([tuas, city], labels = ['tuas', 'city'], autopct = make_autopct([tuas, city]))
       plt.show()

def pm_work_time_portfolio():
       pms = PMs.values()
       idle, meal, on_road, mount_time, offload_time = 0, 0, 0, 0, 0
       for pm in pms:
              i, m, o, mt, ot = pm.work_time_portfolio(False)
              idle += i
              meal += m
              on_road += o
              mount_time += mt
              offload_time += ot
              
       plt.pie([idle, meal, on_road, mount_time, offload_time],
               labels = ['idle', 'meals', 'on road', 'mount', 'offload'],
               labeldistance = 1,
               autopct = '%1.1f%%',
               explode = [0.1, 0.1, 0, 0, 0],
               startangle = 90)
       plt.show()
       
       print('\n-------------# FOR ALL PMS #-------------\n')
       print('\nTime Spent on:\n')
       print('Idle:\t\t\t', round(idle, 2), 'hours', 
             '\nMeals:\t\t\t', meal, 'hours', 
             '\nOn Road:\t\t', round(on_road, 2), 'hours',  
             '\nMounting/Offload:\t', mount_time + offload_time, 'hours')
        
def export_result():
       """
       function:     to export the 2 timings; when it has left the gateway and when it has offloaded at the other location
       input:        None
       returns:      DateFrame with 2 columns; Depart and Arrive
                     Where Depart: The timing of which the container leaves the gate and starts moving towards its destination
                     And Arrive: The timing of which the container has been offloaded at the destination

       """
       c_t = container['time']
       arrive = c_t['arrive']
       depart = c_t['depart']
       exit_gate_to_offload_time = pd.DataFrame({'depart': depart, 'arrive': arrive})
       os.chdir(origin + '/Results')
       exit_gate_to_offload_time.to_csv('tss_results.csv')
       os.chdir(origin)
       
################# EVALUATION OF THE SIMULATION ##################
def plot_vehicle_pattern():
       """
       function:     to plot out the pattern of how
                     the no. of vehicles at a given location
                     changes over each iteration
       input:        None
       returns:      plots and a png file
       """
       os.chdir(origin + '/Results')
       plt.bar(range(len(city_track)),
               city_track,
               label = 'city',
               alpha = 0.9,
               width = 0.7)
       plt.bar(range(len(transit_track)),
               transit_track,
               bottom = city_track,
               label = 'transit',
               alpha = 0.9,
               width = 0.7)
       plt.bar(range(len(tuas_track)),
               tuas_track,
               bottom = [i + j for i, j in zip(city_track, transit_track)],
               label = 'tuas',
               alpha = 0.9,
               width = 0.7)
       plt.ylabel('Proportion'); plt.xlabel('Time')
       plt.legend()
       plt.subplots_adjust(right = 1.5, bottom = 0.1)
       plt.savefig('Vehicle_Pattern.png', bbox_inches = 'tight')
       plt.show()
       os.chdir(origin)

def plot_varying_loads():
       """
       function:     to plot out the amount of varying loads
                     each PM had per transit
       input:        None
       returns:      plots and a png file
       """
       os.chdir(origin + '/Results')
       loads = full_load + half_load + empty_load
       plt.bar(x = range(3),
               height = loads,
               align = 'center',
               color = 'red')
       plt.xticks(ticks = range(3),
                  labels = ['full_load',
                            'half_load',
                            'empty_load'])
       for i in range(3):
              plt.text(x = i - 0.125,
                       y = loads[i] - loads[i]*0.5,
                       s = str(loads[i]),
                       size = 10,
                       color = 'black',
                       fontweight = 'bold')
       plt.ylabel('Count')
       plt.title('How many of what loaded PMs')
       plt.savefig('Varying_Loads.png')
       plt.show()
       os.chdir(origin)

def load_evaluation():
       """
       function:     print out the diagnostics of the different pm loads
       input:        None
       returns:      text file
       """
       print('\nProportion of varying loads:')
       fl, hl, el = full_load[0], half_load[0], empty_load[0]
       total = el + hl + fl
       print('\nProportion of Full Load:\t', round(fl/total, 2))
       print('Proportion of Half Load:\t', round(hl/total, 2))
       print('Proportion of Empty Load:\t', round(el/total, 2))
       
       os.chdir(origin + '/Results')
       text_file = open('Varying_Loads.txt', 'w')
       text_file.writelines(['Proportion of varying loads:',
                             '\nProportion of Full Load:\t' + str(round(fl/total, 2)),
                             '\nProportion of Half Load:\t' + str(round(hl/total, 2)),
                             '\nProportion of Empty Load:\t' + str(round(el/total, 2))])
       text_file.close()
       os.chdir(origin)
       
def plot_dd_back_log():
       """
       function:     to plot out the demand the back log data
       input:        None
       returns:      plots and a png file
       """
       os.chdir(origin + '/Results')
       plt.subplot(2, 2, 1)
       plt.plot(range(1, len(dd_track_city) + 1), dd_track_city)
       plt.title('Demand towards City')
       plt.xlabel('Iteration'); plt.ylabel('Demand')
       plt.subplot(2, 2, 2)
       plt.plot(range(1, len(back_log_track_city) + 1), back_log_track_city)
       plt.title('Back log towards City')
       plt.xlabel('Iteration'); plt.ylabel('Back Log Count')
       plt.subplot(2, 2, 3)
       plt.plot(range(1, len(dd_track_tuas) + 1), dd_track_tuas)
       plt.title('Demand towards Tuas')
       plt.xlabel('Iteration'); plt.ylabel('Demand')
       plt.subplot(2, 2, 4)
       plt.plot(range(1, len(back_log_track_tuas) + 1), back_log_track_tuas)
       plt.title('Back log towards Tuas')
       plt.xlabel('Iteration'); plt.ylabel('Back Log Count')
       plt.subplots_adjust(hspace = 0.8, wspace = 0.8)
       plt.savefig('Demand And Backlog.png')
       plt.show()
       
       print('\nDemand Stats:', '\n###TO CITY###', '\nAvg:\t', round(np.mean(dd_track_city), 2), '\nMax:\t', max(dd_track_city), '\n###TO TUAS###', '\nAvg:\t', round(np.mean(dd_track_tuas), 2), '\nMax:\t', max(dd_track_tuas))
       print('\nBack Log Stats:', '\n###TO CITY###', '\nAvg:\t', round(np.mean(back_log_track_city), 2), '\nMax:\t', max(back_log_track_city), '\n###TO TUAS###', '\nAvg:\t', round(np.mean(back_log_track_tuas), 2), '\nMax:\t', max(back_log_track_tuas))
       
       text_file = open('Demand And Backlog.txt', 'w')
       text_file.writelines(['Demand Stats:', 
                             '\n###TO CITY###', 
                             '\nAvg:\t' + str(round(np.mean(dd_track_city), 2)), 
                             '\nMax:\t' + str(max(dd_track_city)), 
                             '\n###TO TUAS###', 
                             '\nAvg:\t' + str(round(np.mean(dd_track_tuas), 2)),
                             '\nMax:\t' + str(max(dd_track_tuas)),
                             '\n\nBack Log Stats:', 
                             '\n###TO CITY###', 
                             '\nAvg:\t' + str(round(np.mean(back_log_track_city), 2)),
                             '\nMax:\t' + str(max(back_log_track_city)),
                             '\n###TO TUAS###',
                             '\nAvg:\t' + str(round(np.mean(back_log_track_tuas), 2)),
                             '\nMax:\t' + str(max(back_log_track_tuas))])
       text_file.close()
       os.chdir(origin)
        
def plot():
       """
       function:     to plot out all the evaluation models and export all the plots and evaluations
       input:        None
       returns:      text and png files alongside the plots in the console
       """
       # vehicle location trends
       plot_vehicle_pattern()
       
       # diagnostics for loads that were carried
       plot_varying_loads()
       
       # text for load evaluation
       load_evaluation()
       
       # backlog and demand diagnostics
       plot_dd_back_log()
       
       # how many containers have been moved
       total_containers = len(container['moved_index']) - container['moved_index'].count('init')
       moved_1s = container['moved_index'].count(1)
       not_moved_0s = container['moved_index'].count(0)
       couldnt_move_n2 = container['moved_index'].count('N2')
       print('\nStatus of Containers (Count):')
       print('Moved:    ', moved_1s, '   \t(' + str(round((moved_1s / total_containers)*100, 2)) + '%)')
       print('Untouched:', not_moved_0s, '   \t(' + str(round((not_moved_0s / total_containers)*100, 2)) + '%)')
       print('Missed:   ', couldnt_move_n2, '   \t(' + str(round((couldnt_move_n2 / total_containers)*100, 2)) + '%)')
       
       os.chdir(origin + '/Results/')
       text_file = open('Container_Diagnostics.txt', 'w')
       text_file.writelines(['Status of Containers (Count):',
                             '\nMoved:    ' + str(moved_1s) + '   \t(' + str(round((moved_1s / total_containers)*100, 2)) + '%)',
                             '\nUntouched:' + str(not_moved_0s) + '   \t(' + str(round((not_moved_0s / total_containers)*100, 2)) + '%)',
                             '\nMissed:   ' + str(couldnt_move_n2) + '   \t(' + str(round((couldnt_move_n2 / total_containers)*100, 2)) + '%)'])
       text_file.close()
       os.chdir(origin)
       

###################################################################

def simulate_shifting(df, n = 1000, bl = 100, init = 250):
       """
       function:     simulates the shifting of containers between tuas and city
       input:        scenario data in the form of a dataframe
       returns:      DataFrame [Refer to export_result() function to find out what's being exported]

       Goal:  I'd say it's to minimize the number of half and empty loads
              while trying to maximize full loads.

       """
       print('Commencement of Simulation with parameters:\n', 
             str(n) + ' Observations\n', 
             str(bl) + ' Back-log, and\n', 
             str(init) + ' for Initialisation')
       # this is to record the movements of the containers
       global container 
       container['moved_index'] = [0]*n
       container['time']['depart'] = [0]*n
       container['time']['arrive'] = [0]*n
       container['excess'] = ['0']*n

       for i in range(bl, n):
              # this is to 'naturally' initialize the variables
              if i == init:
                     # containers that have made the full trip are considered used for initialisation. those that are not will be in transit or considered backlog
                     container_bool = np.where(np.asarray(container['time']['arrive'][:init + 1]) == 0, False, True)
                     for i, b in enumerate(container_bool):
                            if b:
                                   container['moved_index'][i], container['time']['depart'][i], container['time']['arrive'][i], container['excess'][i] = 'init', 'init', 'init', 'init'

                     # restarting the tracking of PMs at Tuas, City and Transit
                     temp = transit_track.pop()
                     transit_track.clear()
                     transit_track.append(temp)
                     temp = tuas_track.pop()
                     tuas_track.clear()
                     tuas_track.append(temp)
                     temp = city_track.pop()
                     city_track.clear()
                     city_track.append(temp)

                     full_load[0] = 0
                     half_load[0] = 0
                     empty_load[0] = 0

              # tracking the counts at each location
              tuas_track_append(PMs_track['tuas'])
              city_track_append(PMs_track['city'])
              transit_track_append(len(PMs_track['transit']['time']))

              # structure observation data
              going_to, container_size, disc_dt, connect_time = df.iat[i, 1], df.iat[i, 2], df.iat[i, 3], df.iat[i, 4] 

              # update the PMs that are on transit, to check if they've reached the other location
              transit = PMs_track['transit']
              if transit['time']:
                     # declaring the rest of the variables
                     transit_time, transit_dest, transit_index, transit_size = transit['time'], transit['dest'], transit['index'], transit['size']
                     
                     # getting the duration each PM has been on transit for
                     trans_updater = list(map(lambda x: get_hours(disc_dt - x), transit_time))
                     # the function returns a boolean list of the PMs that have returned or not
                     trans_updater = pm_arrival_updater(trans_updater, transit_size, transit_time)
                     
                     # update the venues and container
                     finished_pm_index = [a for a, b in enumerate(trans_updater) if b == False]
                     for index in finished_pm_index:
                            # update location count
                            PMs_track[transit_dest[index]] += 1
                            
                            # update PMs
                            arrived_pm = list(filter(lambda x: transit_index[index] in x.work_log['container'], PMs.values()))[0] 
                            arrived_pm.location, arrived_pm.current_dest = arrived_pm.current_dest, None
                            
                            arrived_pm.work_log['arrive'] += [disc_dt]

                            # update containers
                            if type(transit_index[index]) != str:
                                   if type(transit_index[index]) == list:
                                          arrival_index_1, arrival_index_2 = transit_index[index]
                                          container['time']['arrive'][arrival_index_1] = disc_dt
                                          container['excess'][arrival_index_1] = df.iat[arrival_index_1, 4] - get_hours(disc_dt - container['time']['depart'][arrival_index_1] - datetime.timedelta(minutes = 15))

                                          container['time']['arrive'][arrival_index_2] = disc_dt
                                          container['excess'][arrival_index_2] = df.iat[arrival_index_2, 4] - get_hours(disc_dt - container['time']['depart'][arrival_index_2] - datetime.timedelta(minutes = 15))
                                   else:
                                          arrival_index = transit_index[index]
                                          container['time']['arrive'][arrival_index] = disc_dt
                                          container['excess'][arrival_index] = df.iat[arrival_index, 4] - get_hours(disc_dt - container['time']['depart'][arrival_index] - datetime.timedelta(minutes = 15))
                     
                     PMs_track['transit']['time'] = list(compress(transit_time, trans_updater))
                     PMs_track['transit']['dest'] = list(compress(transit_dest, trans_updater))
                     PMs_track['transit']['index'] = list(compress(transit_index, trans_updater))
                     PMs_track['transit']['size'] = list(compress(transit_size, trans_updater))

              # checking of demand and backlog
              # look before
              back_log_to_city = sum((df.iloc[[ind for ind, stat in enumerate(container['moved_index'][:i]) if stat == 0], :])['DIRECTION_shift'] == 'EB_City')
              back_log_to_tuas = sum((df.iloc[[ind for ind, stat in enumerate(container['moved_index'][:i]) if stat == 0], :])['DIRECTION_shift'] == 'WB_Tuas')
              # look after
              dd_to_tuas, dd_to_city = 0, 0
              dd_present_time, dd_advance_time = disc_dt, disc_dt
              count = i + 1
              while count < n - 1 and get_hours(dd_advance_time - dd_present_time) <= forward_dd:
                     if df.iat[count, 1] == 'EB_City':
                            dd_to_city += 1
                     else:
                            dd_to_tuas += 1
                     count += 1
                     dd_advance_time = df.iat[count, 3]
              back_log_track_city_append(back_log_to_city)
              back_log_track_tuas_append(back_log_to_tuas)
              dd_track_city_append(dd_to_city)
              dd_track_tuas_append(dd_to_tuas)

              # checking on the number of PMs otw to each location
              transit_to_dest = get_transit_dest_count(PMs)
              transit_to_city, transit_to_tuas = transit_to_dest['city'], transit_to_dest['tuas']

              # updating of unmoved containers
              if 0 in container['moved_index'][:i]:
                     # look for the indexes of the containers that haven't been moved
                     index_zero = [ind for ind, e in enumerate(container['moved_index'][:i]) if e == 0]
                     # sort based on connection time (shortest to longest)
                     index_zero.sort(key = lambda x: df.iat[x, 4] - get_hours(disc_dt - df.iat[x, 3]))
                     # based on the container indexes, i look up its information based on the dataframe
                     for j in index_zero:
                            # will settle the container that has the shortest connection time remaining (from the current time of pm activation to load_dt)
                            zero_going_to, zero_container_size, zero_disc_dt, zero_connect_time = df.iat[j, 1], df.iat[j, 2], df.iat[j, 3], df.iat[j, 4]
                            
                            # while updating the connection time based on when it arrived to the port till the time we can activate a PM to send it
                            zero_connect_time = zero_connect_time - get_hours(disc_dt - zero_disc_dt)
                            if zero_container_size >= 22:
                                   zero_container_size = 'full'
                            else:
                                   zero_container_size = 'half'
                            # if we missed it, we mark as N2
                            if zero_connect_time <= travel_duration(zero_container_size, zero_disc_dt):
                                   container['moved_index'][j] = 'N2'

                            # if it's a full load or there's not much time left, we just activate an available PM (if there are any) to send it over
                            if zero_connect_time < threshold_connectingtime or zero_container_size == 'full' or container['moved_index'][j] == 'N2':
                                   if zero_going_to == 'EB_City':
                                          # get a PM
                                          duty_pm = check_pm_avail(disc_dt, 'city', zero_container_size)
                                          if PMs_track['tuas'] > 0 and duty_pm:
                                                 # update duty_pm
                                                 duty_pm.location = 'transit'
                                                 duty_pm.current_dest = 'city'
                                                 duty_pm.trips_count[zero_container_size] += 1
                                                 duty_pm.trips_count['dest'] += ['city']
                                                 duty_pm.work_log['depart'] += [disc_dt]
                                                 duty_pm.work_log['container'] += [j]

                                                 PMs_track['tuas'] -= 1

                                                 PMs_track['transit']['time'] += [disc_dt]
                                                 PMs_track['transit']['dest'] += ['city']
                                                 PMs_track['transit']['index'] += [j]
                                                 PMs_track['transit']['size'] += [zero_container_size]

                                                 if container['moved_index'][j] == 0:
                                                        container['moved_index'][j] = 1
                                                 container['time']['depart'][j] = disc_dt + datetime.timedelta(minutes = 15)
                                                 if zero_container_size == 'full':
                                                        full_load[0] += 1
                                                 else:
                                                        half_load[0] += 1
                                   # going tuas
                                   else:
                                          # get a PM
                                          duty_pm = check_pm_avail(disc_dt, 'tuas', zero_container_size)
                                          if PMs_track['city'] > 0 and duty_pm:
                                                 # update duty_pm
                                                 duty_pm.location = 'transit'
                                                 duty_pm.current_dest = 'tuas'
                                                 duty_pm.trips_count[zero_container_size] += 1
                                                 duty_pm.trips_count['dest'] += ['tuas']
                                                 duty_pm.work_log['depart'] += [disc_dt]
                                                 duty_pm.work_log['container'] += [j]

                                                 PMs_track['city'] -= 1

                                                 PMs_track['transit']['time'] += [disc_dt]
                                                 PMs_track['transit']['dest'] += ['tuas']
                                                 PMs_track['transit']['index'] += [j]
                                                 PMs_track['transit']['size'] += [zero_container_size]

                                                 if container['moved_index'][j] == 0:
                                                        container['moved_index'][j] = 1
                                                 container['time']['depart'][j] = disc_dt + datetime.timedelta(minutes = 15)
                                                 if zero_container_size == 'full':
                                                        full_load[0] += 1
                                                 else:
                                                        half_load[0] += 1

                     # check if there're still unmoved containers after moving the urgent and full loads
                     # send the half loads as full loads
                     if 0 in container['moved_index'][:i]:
                            index_zero = [ind for ind, e in enumerate(container['moved_index'][:i]) if e == 0]
                            # only handling half containers
                            index_zero = [x for x in index_zero if df.iat[x, 2] == 20]
                            
                            index_zero_to_tuas = [x for x in index_zero if df.iat[x, 1] == 'WB_Tuas'] # list(filter(lambda x: df.iat[x, 1] == 'WB_Tuas', index_zero))
                            
                            # sort by connection time remaining (shortest to longest)
                            index_zero_to_tuas.sort(key = lambda x: df.iat[x, 4] - get_hours(disc_dt - df.iat[x, 3])) 
                            
                            index_zero_to_city = [x for x in index_zero if df.iat[x, 1] == 'EB_City'] # list(filter(lambda x: df.iat[x, 1] == 'EB_City', index_zero))
                            # sort by connection time remaining (shortest to longest)
                            index_zero_to_city.sort(key = lambda x: df.iat[x, 4] - get_hours(disc_dt - df.iat[x, 3])) 
                            
                            if index_zero_to_tuas:
                                   for j in range(1, len(index_zero_to_tuas), 2):
                                          h = index_zero_to_tuas[j]
                                          h_index = index_zero_to_tuas[j - 1]
                                          
                                          duty_pm = check_pm_avail(disc_dt, 'tuas', 'full')
                                          if PMs_track['city'] > 0 and duty_pm:
                                                 # update duty_pm
                                                 duty_pm.location = 'transit'
                                                 duty_pm.current_dest = 'tuas'
                                                 duty_pm.trips_count['full'] += 1
                                                 duty_pm.trips_count['dest'] += ['tuas']
                                                 duty_pm.work_log['depart'] += [disc_dt]
                                                 duty_pm.work_log['container'] += [[h, h_index]]

                                                 PMs_track['tuas'] -= 1

                                                 PMs_track['transit']['time'] += [disc_dt]
                                                 PMs_track['transit']['dest'] += ['tuas']
                                                 PMs_track['transit']['index'] += [[h, h_index]]
                                                 PMs_track['transit']['size'] += ['full']

                                                 container['moved_index'][h] = 1
                                                 container['moved_index'][h_index] = 1
                                                 container['time']['depart'][h] = disc_dt + datetime.timedelta(minutes = 15)
                                                 container['time']['depart'][h_index] = disc_dt + datetime.timedelta(minutes = 15)

                                                 full_load[0] += 1
                                   
                            if index_zero_to_city:
                                   for j in range(1, len(index_zero_to_city), 2):
                                          h = index_zero_to_city[j]
                                          h_index = index_zero_to_city[j - 1]
                                          
                                          duty_pm = check_pm_avail(disc_dt, 'city', 'full')
                                          if PMs_track['tuas'] > 0 and duty_pm:
                                                 # update duty_pm
                                                 duty_pm.location = 'transit'
                                                 duty_pm.current_dest = 'city'
                                                 duty_pm.trips_count['full'] += 1
                                                 duty_pm.trips_count['dest'] += ['city']
                                                 duty_pm.work_log['depart'] += [disc_dt]
                                                 duty_pm.work_log['container'] += [[h, h_index]]
                                                 
                                                 PMs_track['city'] -= 1
                                                 
                                                 PMs_track['transit']['time'] += [disc_dt]
                                                 PMs_track['transit']['dest'] += ['city']
                                                 PMs_track['transit']['index'] += [[h, h_index]]
                                                 PMs_track['transit']['size'] += ['full']
                                                 
                                                 container['moved_index'][h] = 1
                                                 container['moved_index'][h_index] = 1
                                                 container['time']['depart'][h] = disc_dt + datetime.timedelta(minutes = 15)
                                                 container['time']['depart'][h_index] = disc_dt + datetime.timedelta(minutes = 15)

                                                 full_load[0] += 1

              # for full length containers
              if container_size > 22:
                     # initiate PM
                     if going_to == 'EB_City':
                            # get a PM
                            duty_pm = check_pm_avail(disc_dt, 'city', 'full')
                            if PMs_track['tuas'] > 0 and duty_pm:
                                   # update duty_pm
                                   duty_pm.location = 'transit'
                                   duty_pm.current_dest = 'city'
                                   duty_pm.trips_count['full'] += 1
                                   duty_pm.trips_count['dest'] += ['city']
                                   duty_pm.work_log['depart'] += [disc_dt]
                                   duty_pm.work_log['container'] += [i]

                                   PMs_track['tuas'] -= 1

                                   PMs_track['transit']['time'] += [disc_dt]
                                   PMs_track['transit']['dest'] += ['city']
                                   PMs_track['transit']['index'] += [i]
                                   PMs_track['transit']['size'] += ['full']

                                   container['moved_index'][i] = 1
                                   container['time']['depart'][i] = disc_dt + datetime.timedelta(minutes = 15)

                                   full_load[0] += 1
                     else:
                            # get a PM
                            duty_pm = check_pm_avail(disc_dt, 'tuas', 'full')
                            if PMs_track['city'] > 0 and duty_pm:
                                   # update duty_pm
                                   duty_pm.location = 'transit'
                                   duty_pm.current_dest = 'tuas'
                                   duty_pm.trips_count['full'] += 1
                                   duty_pm.trips_count['dest'] += ['tuas']
                                   duty_pm.work_log['depart'] += [disc_dt]
                                   duty_pm.work_log['container'] += [i]

                                   PMs_track['city'] -= 1

                                   PMs_track['transit']['time'] += [disc_dt]
                                   PMs_track['transit']['dest'] += ['tuas']
                                   PMs_track['transit']['index'] += [i]
                                   PMs_track['transit']['size'] += ['full']

                                   container['moved_index'][i] = 1
                                   container['time']['depart'][i] = disc_dt + datetime.timedelta(minutes = 15)

                                   full_load[0] += 1

              # for half length containers
              else:
                     # finding other half loads that are available
                     index, index_going_to, index_container_size = None, None, None
                     if 0 in container['moved_index'][:i]:
                            # search for the first 0 then start from there. so we slice from [first zero index:i] (can be O(logn))
                            # settling any prior container of size 20 that's yet to be shipped
                            index_twenties = [j for j, e in enumerate(container['moved_index'][:i]) if e == 0]
                            l = len(index_twenties)
                            index_twenties = iter(index_twenties)
                            for c in range(l): 
                                   c_i = next(index_twenties)
                                   # index_obs = df.iloc[c_i, :]
                                   index, index_going_to, index_container_size = c_i, df.iat[c_i, 1], df.iat[c_i, 2]
                                   if index_going_to == going_to and index_container_size <= 22:
                                          break

                     # if there are other half loads available
                     if index_going_to == going_to and index_container_size <= 22:
                            if going_to == 'EB_City':
                                   # get a PM
                                   duty_pm = check_pm_avail(disc_dt, 'city', 'full')
                                   if PMs_track['tuas'] > 0 and duty_pm:
                                          # update duty_pm
                                          duty_pm.location = 'transit'
                                          duty_pm.current_dest = 'city'
                                          duty_pm.trips_count['full'] += 1
                                          duty_pm.trips_count['dest'] += ['city']
                                          duty_pm.work_log['depart'] += [disc_dt]
                                          duty_pm.work_log['container'] += [[i, index]]

                                          PMs_track['tuas'] -= 1

                                          PMs_track['transit']['time'] += [disc_dt]
                                          PMs_track['transit']['dest'] += ['city']
                                          PMs_track['transit']['index'] += [[i, index]]
                                          PMs_track['transit']['size'] += ['full']

                                          container['moved_index'][i] = 1
                                          container['moved_index'][index] = 1
                                          container['time']['depart'][i] = disc_dt + datetime.timedelta(minutes = 15)
                                          container['time']['depart'][index] = disc_dt + datetime.timedelta(minutes = 15)

                                          full_load[0] += 1
                            else:
                                   # get a PM
                                   duty_pm = check_pm_avail(disc_dt, 'tuas', 'full')
                                   if PMs_track['city'] > 0 and duty_pm:
                                          duty_pm.location = 'transit'
                                          duty_pm.current_dest = 'tuas'
                                          duty_pm.trips_count['full'] += 1
                                          duty_pm.trips_count['dest'] += ['tuas']
                                          duty_pm.work_log['depart'] += [disc_dt]
                                          duty_pm.work_log['container'] += [[i, index]]

                                          PMs_track['city'] -= 1

                                          PMs_track['transit']['time'] += [disc_dt]
                                          PMs_track['transit']['dest'] += ['tuas']
                                          PMs_track['transit']['index'] += [[i, index]]
                                          PMs_track['transit']['size'] += ['full']

                                          container['moved_index'][i] = 1
                                          container['moved_index'][index] = 1
                                          container['time']['depart'][i] = disc_dt + datetime.timedelta(minutes = 15)
                                          container['time']['depart'][index] = disc_dt + datetime.timedelta(minutes = 15)

                                          full_load[0] += 1

                     # if there're no other half loads available
                     else:
                            if going_to == 'EB_City':
                                   if (PMs_track[going_to[3:].lower()] < threshold_vehicle_half and dd_to_tuas > threshold_dd) or connect_time < threshold_connectingtime: # or ((transit_to_tuas/back_log_to_city >= threshold_transit_to_dest) and back_log_to_city > threshold_back_log):
                                          # get a PM
                                          duty_pm = check_pm_avail(disc_dt, 'city', 'half')
                                          if PMs_track['tuas'] > 0 and duty_pm:
                                                 # update duty_pm
                                                 duty_pm.location = 'transit'
                                                 duty_pm.current_dest = 'city'
                                                 duty_pm.trips_count['half'] += 1
                                                 duty_pm.trips_count['dest'] += ['city']
                                                 duty_pm.work_log['depart'] += [disc_dt]
                                                 duty_pm.work_log['container'] += [i]

                                                 PMs_track['tuas'] -= 1

                                                 PMs_track['transit']['time'] += [disc_dt]
                                                 PMs_track['transit']['dest'] += ['city']
                                                 PMs_track['transit']['index'] += [i]
                                                 PMs_track['transit']['size'] += ['half']

                                                 container['moved_index'][i] = 1
                                                 container['time']['depart'][i] = disc_dt + datetime.timedelta(minutes = 15)
                                                 half_load[0] += 1
                            else:
                                   if (PMs_track[going_to[3:].lower()] < threshold_vehicle_half and dd_to_city > threshold_dd) or connect_time < threshold_connectingtime:
                                          # get a PM
                                          duty_pm = check_pm_avail(disc_dt, 'tuas', 'half')
                                          if PMs_track['city'] > 0 and duty_pm:
                                                 # update duty_pm
                                                 duty_pm.location = 'transit'
                                                 duty_pm.current_dest = 'tuas'
                                                 duty_pm.trips_count['half'] += 1
                                                 duty_pm.trips_count['dest'] += ['tuas']
                                                 duty_pm.work_log['depart'] += [disc_dt]
                                                 duty_pm.work_log['container'] += [i]

                                                 PMs_track['city'] -= 1

                                                 PMs_track['transit']['time'] += [disc_dt]
                                                 PMs_track['transit']['dest'] += ['tuas']
                                                 PMs_track['transit']['index'] += [i]
                                                 PMs_track['transit']['size'] += ['half']

                                                 container['moved_index'][i] = 1
                                                 container['time']['depart'][i] = disc_dt + datetime.timedelta(minutes = 15)
                                                 half_load[0] += 1

              # sending empty PMs to city
              if dd_to_tuas > threshold_dd_empty and transit_to_city < (threshold_transit_to_dest * dd_to_tuas):
                     if PMs_track['tuas'] >= threshold_vehicle_half:
                            for p in range(move_over):
                                   # get a PM
                                   duty_pm = check_pm_avail(disc_dt, 'city', 'empty')
                                   if duty_pm:
                                          # update duty_pm
                                          duty_pm.location = 'transit'
                                          duty_pm.current_dest = 'city'
                                          duty_pm.trips_count['empty'] += 1
                                          duty_pm.trips_count['dest'] += ['city']
                                          duty_pm.work_log['depart'] += [disc_dt]
                                          duty_pm.work_log['container'] += ['empty' + str(p) + '|' + str(i)]

                                          PMs_track['tuas'] -= 1

                                          PMs_track['transit']['time'] += [disc_dt]
                                          PMs_track['transit']['dest'] += ['city']
                                          PMs_track['transit']['index'] += ['empty' + str(p) + '|' + str(i)]
                                          PMs_track['transit']['size'] += ['empty']

                                          empty_load[0] += move_over
              
              # sending empty PMs to tuas
              if dd_to_city > threshold_dd_empty and transit_to_tuas < (threshold_transit_to_dest * dd_to_city):
                     if PMs_track['city'] >= threshold_vehicle_half:
                            for p in range(move_over):
                                   # get a PM
                                   duty_pm = check_pm_avail(disc_dt, 'tuas', 'empty')
                                   if duty_pm:
                                          # update duty_pm
                                          duty_pm.location = 'transit'
                                          duty_pm.current_dest = 'tuas'
                                          duty_pm.trips_count['empty'] += 1
                                          duty_pm.trips_count['dest'] += ['tuas']
                                          duty_pm.work_log['depart'] += [disc_dt]
                                          duty_pm.work_log['container'] += ['empty' + str(i) + '|' + str(p)]

                                          PMs_track['city'] -= 1

                                          PMs_track['transit']['time'] += [disc_dt]
                                          PMs_track['transit']['dest'] += ['city']
                                          PMs_track['transit']['index'] += ['empty' + str(i) + '|' + str(p)]
                                          PMs_track['transit']['size'] += ['empty']

                                          empty_load[0] += move_over
              # Loading Bar
              stop_values = list(map(lambda x: floor(x), np.linspace(bl, n - 1, 11)))
              if i in stop_values:
                     prop_done = stop_values.index(i)
                     print('[' + '###'*prop_done + '   '*(10 - prop_done) + ']' + '  ' + str(prop_done*10) + '% done')
       
       # to export a .csv file
       export_result()
       plot()
