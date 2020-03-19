"""
[2/2] of the module that replaced `TuasShiftingSimulation.py`.
"""
import os
import pandas as pd
import datetime
import numpy as np
from itertools import compress
import matplotlib.pyplot as plt
from math import floor

# PM Class
class PM():
       """
       This is a PM class.
       It holds the values each PM requires for tracking and diagnostics
       
       input:        where the pm starts from (tuas/city)
                     which hours this pm works for
                     which shift this pm works, for convenience sake
       """
       def __init__(self, index, starting_location, working_hours, work_shift):
              self.index = index
              self.origin = starting_location
              self.location = starting_location
              self.current_dest = None
              self.trips_count = {'full': 0, # trip count for type
                                  'half': 0,
                                  'empty': 0,
                                  'dest': []} # trip count for destination
              self.working_hours = working_hours
              self.work_shift = work_shift
              self.work_log = {'depart': [], # to track when it departs for transport
                               'arrive': [], # and when it arrives at location
                               'container': []} # to track which PM took which container
       
       def get_hours(self, timedelta):
              """
              function:     to convert a timedelta object into hours
              input:        timedelta object
              returns:      time in terms of hours
              """
              result = timedelta.total_seconds()
              result = (result / 60) / 60
              result = round(result, 2)
              return result
       
       def flatten(self, container):
              """
              function:     to flatten a nested list into a list
              input:        list
              output:       flatten object. return as list(flatten(input))
              """
              for i in container:
                     if isinstance(i, (list,tuple)):
                            for j in self.flatten(i):
                                   yield j
                     else:
                            yield i

       def set_working_hours(self, hours):
              """
              function:     set the working hours for the PM vehicle
              input:        a list of the hours (out of 24 hours) that the PM will be working for
              output:       None. Will update the working hours of the PM
              """
              self.working_hours = hours
              

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

              # flexi
              work_shift_meal_times = {'7m': {'0': 11, '1': 12},
                                       '7n': {'0': 1, '1': 2},
                                       '8m': 11,
                                       '8n': 1,
                                       '9m': 12,
                                       '9n': 2}
              meal_shift_d = str(int(np.random.rand() + 0.5))
              work_shift_meal_times['7m'], work_shift_meal_times['7n'] = work_shift_meal_times['7m'][meal_shift_d], work_shift_meal_times['7n'][meal_shift_d]

              # make sure there's a 2 hour gap before they panggang
              if self.working_hours[current_hour] == 1 and self.working_hours[(current_hour + 1) % 24] == 1 and self.working_hours[(current_hour + 2) % 24] == 1:
                     # 1 hour gap before they go off for lunch
                     if current_hour != work_shift_meal_times[self.work_shift] and self.working_hours[(work_shift_meal_times[self.work_shift] + 1) % 24] == 1:
                            return True
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
                            clean_a = [x for x in a if (x.year == curr_day.year and x.month == curr_day.month and x.day == curr_day.day)]
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
                            duration = self.get_hours(i['depart'][j] - i['arrive'][j])
                            total_duration += duration
                            if duration <= 0:
                                   continue
                            print('From:', i['arrive'][j], '\t', 'To:', i['depart'][j], '\tDuration:', duration)
                     if len(i['depart']) != n:
                            end = (self.get_hours(i['depart'][-1] - i['depart'][-2]) - 2)
                            total_duration += end
              print('\nTotal Duration:', round(total_duration, 2), '\n')
              return days_log

       def retrieve_container_indexes(self):
              """
              function:     returns a flattened list of the container indexes (wrt to the dataframe)
              input:        nothing
              output:       a list of indexes
              """
              return [x for x in self.flatten(self.work_log['container']) if type(x) != str] # list(filter(lambda x: type(x) != str, flatten(self.work_log['container'])))

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
                            duration = self.get_hours(i['depart'][j] - i['arrive'][j])
                            total_idle += duration
                            if duration <= 0:
                                   continue
                     if m != n:
                            total_idle += (self.get_hours(i['depart'][-1] - i['depart'][-2]) - 2)
                            
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

# Simulation Class
class Simulation():
       """
       This is the simulation class that will be used to run the simulation model
       input:        
              tuas_vehicles = initial number of vehicles at tuas
              city_vehicles = initial number of vehicles at city
              threshold_connectingtime = at how many hours is it considered urgent
              threshold_back_log = what's the limit of backlog that's tolerable
              threshold_dd = what's the limit of demand that's tolerable
              threshold_dd_empty = what's the limit of demand that's tolerable for moving an empty PM
              threshold_empty_movement = what's the the amount of PM at a location that would trigger
                                          a movement for an empty PM given high demand and backlog
              forward_dd = how many hours to look ahead to check demand
              threshold_vehicle_half = at how many hours is it considered urgent to send half a load by itself
              move_over = how many empty PMs to moveover at a time
       """
       def __init__(self, tuas_vehicles = 150, 
                    city_vehicles = 150, 
                    threshold_connectingtime = 12, 
                    threshold_back_log = 58, 
                    threshold_dd = 55, 
                    threshold_dd_empty = 75, 
                    threshold_empty_movement = 2, 
                    forward_dd = 2, 
                    threshold_vehicle_half = 25,
                    move_over = 1):
              # how many vehicles at each location at the start
              self.tuas_vehicles = tuas_vehicles
              self.city_vehicles = city_vehicles
              
              # at what thresholds should we start prioritising sending the container over
              self.threshold_connectingtime = threshold_connectingtime
              self.threshold_back_log = threshold_back_log
              self.threshold_dd = threshold_dd
              self.threshold_dd_empty = threshold_dd_empty
              self.threshold_empty_movement = threshold_empty_movement
       
              # how many hours forward should we look for the demand
              self.forward_dd = forward_dd
              
              # at what quantity of vehicles should we start sending over empty PMs
              self.threshold_vehicle_half = threshold_vehicle_half # if the other side has this many or below, it'll send half PMs
              
              # how many PMs to move over, when either side is low in PMs
              self.move_over = move_over

              # tracking of Prime Movers as a whole
              self.PMs_track = {'tuas': tuas_vehicles,         # stands for Prime Movers
                                'city': city_vehicles,
                                'transit': {'dest': [], 'time' : [], 'index': [], 'size': []}
                                }
              
              # tracking containers
                            
              self.container = {'moved_index': [],
                                'time': {'depart': [], 'arrive': []},
                                'excess': []
                                }

              # to track the progression of the amount of PMs at each location
              # for plotting; debugging
              self.transit_track = []
              self.tuas_track = []
              self.city_track = []
              self.back_log_track_city = []
              self.back_log_track_tuas = []
              self.dd_track_city = []
              self.dd_track_tuas = []

              # track how many full, half or empty vehicles that have been pushed off
              self.full_load = 0
              self.half_load = 0
              self.empty_load = 0

              # Initialize PMs
              self.PMs = {}
              for i in range(1, 301):
                     if i <= 150:
                            if i <= 25:
                                   self.PMs['PM_' + str(i)] = PM(i, 'city', [0]*7 + [1]*12 + [0]*5, '7m')
                            elif i <= 50:
                                   self.PMs['PM_' + str(i)] = PM(i, 'city', [1]*7 + [0]*12 + [1]*5, '7n')
                            elif i <= 75:
                                   self.PMs['PM_' + str(i)] = PM(i, 'city', [0]*8 + [1]*12 + [0]*4, '8m')
                            elif i <= 100:
                                   self.PMs['PM_' + str(i)] = PM(i, 'city', [1]*8 + [0]*12 + [1]*4, '8n')
                            elif i <= 125:
                                   self.PMs['PM_' + str(i)] = PM(i, 'city', [0]*9 + [1]*12 + [0]*3, '9m')
                            else:
                                   self.PMs['PM_' + str(i)] = PM(i, 'city', [1]*9 + [0]*12 + [1]*3, '9n')
                     else:
                            if i <= 175:
                                   self.PMs['PM_' + str(i)] = PM(i, 'tuas', [0]*7 + [1]*12 + [0]*5, '7m')
                            elif i <= 200:
                                   self.PMs['PM_' + str(i)] = PM(i, 'tuas', [1]*7 + [0]*12 + [1]*5, '7n')
                            elif i <= 225:
                                   self.PMs['PM_' + str(i)] = PM(i, 'tuas', [0]*8 + [1]*12 + [0]*4, '8m') 
                            elif i <= 250:
                                   self.PMs['PM_' + str(i)] = PM(i, 'tuas', [1]*8 + [0]*12 + [1]*4, '8n')
                            elif i <= 275:
                                   self.PMs['PM_' + str(i)] = PM(i, 'tuas', [0]*9 + [1]*12 + [0]*3, '9m')
                            else:
                                   self.PMs['PM_' + str(i)] = PM(i, 'tuas', [1]*9 + [0]*12 + [1]*3, '9n')
       
       ############## HELPER FUNCTIONS FOR THE SIMULATION ################
       def PM_locations(self):
              """
              function:     get the locations of all the PMs
              input:        None
              returns:      a string that states the location of all the PMs
              """
              n_transit = len(self.PMs_track['transit']['time'])
              n_city = self.PMs_track['city']
              n_tuas = self.PMs_track['tuas']
              print('Transit:', n_transit, 'City:', n_city, 'Tuas:', n_tuas)
              
       def get_transit_dest_count(self):
              """
              function:     counts the number of PMs that are currently on their way to a particular location
              input:        dictionary of PMs
              output:       the count of PMs that are on their way over to Tuas or City
              """
              list_of_PMs = [pm for pm in self.PMs.values() if pm.location == 'transit']
              city = list(map(lambda x: x.current_dest, list_of_PMs)).count('city')
              tuas = list(map(lambda x: x.current_dest, list_of_PMs)).count('tuas')
              return {'city': city, 'tuas': tuas}

       def container_info(self, data, container_id, info): # not in use
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
       
       def get_hours(self, timedelta):
              """
              function:     to convert a timedelta object into hours
              input:        timedelta object
              returns:      time in terms of hours
              """
              result = timedelta.total_seconds()
              result = (result / 60) / 60
              result = round(result, 2)
              return result
       
       def check_pm_avail(self, time, dest, trip_type):
              """
              function:     get an available PM to do a transfer
              input:        timing, destination, type of trip (full, half, empty)
              output:       either the id of an available PM or False
              """
              ds = {'city': 'tuas', 'tuas': 'city'}
              list_of_PMs = [x for x in self.PMs.values() if (x.able_to_work(time) and x.location == ds[dest])]
       
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
       
       def pm_arrival_updater(self, duration_out, size, timing):
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
              result = [boolean_generator(i) for i in range(len(duration_out))]
              result = np.array(result)
              return result
       
       def travel_duration(self, size, timing):
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
       
       def shift_change_analysis(self, shift):
              """
              function:     to analyse the PMs during the shift change period
              input:        which shift to analyse
              output:       the analysis and breakdown of all the PMs during that particular shift change
              """
              pms = self.PMs.values()
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
       
       def pm_work_time_portfolio(self):
              pms = self.PMs.values()
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
               
       def export_result(self):
              """
              function:     to export the 2 timings; when it has left the gateway and when it has offloaded at the other location
              input:        None
              returns:      DateFrame with 2 columns; Depart and Arrive
                            Where Depart: The timing of which the container leaves the gate and starts moving towards its destination
                            And Arrive: The timing of which the container has been offloaded at the destination
       
              """
              c_t = self.container['time']
              arrive = c_t['arrive']
              depart = c_t['depart']
              exit_gate_to_offload_time = pd.DataFrame({'depart': depart, 'arrive': arrive})
              os.chdir(origin + '/Results')
              exit_gate_to_offload_time.to_csv('tss_results.csv')
              os.chdir(origin)
              
       ################# EVALUATION OF THE SIMULATION ##################
       def plot_vehicle_pattern(self):
              """
              function:     to plot out the pattern of how
                            the no. of vehicles at a given location
                            changes over each iteration
              input:        None
              returns:      plots and a png file
              """
              os.chdir(origin + '/Results')
              plt.bar(range(len(self.city_track)),
                      self.city_track,
                      label = 'city',
                      alpha = 0.9,
                      width = 0.7)
              plt.bar(range(len(self.transit_track)),
                      self.transit_track,
                      bottom = self.city_track,
                      label = 'transit',
                      alpha = 0.9,
                      width = 0.7)
              plt.bar(range(len(self.tuas_track)),
                      self.tuas_track,
                      bottom = [i + j for i, j in zip(self.city_track, self.transit_track)],
                      label = 'tuas',
                      alpha = 0.9,
                      width = 0.7)
              plt.ylabel('Proportion'); plt.xlabel('Time')
              plt.legend()
              plt.subplots_adjust(right = 1.5, bottom = 0.1)
              plt.savefig('Vehicle_Pattern.png', bbox_inches = 'tight')
              plt.show()
              os.chdir(origin)
       
       def plot_varying_loads(self):
              """
              function:     to plot out the amount of varying loads
                            each PM had per transit
              input:        None
              returns:      plots and a png file
              """
              os.chdir(origin + '/Results')
              loads = [self.full_load, self.half_load, self.empty_load]
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
       
       def load_evaluation(self):
              """
              function:     print out the diagnostics of the different pm loads
              input:        None
              returns:      text file
              """
              print('\nProportion of varying loads:')
              fl, hl, el = self.full_load, self.half_load, self.empty_load
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
              
       def plot_dd_back_log(self):
              """
              function:     to plot out the demand the back log data
              input:        None
              returns:      plots and a png file
              """
              os.chdir(origin + '/Results')
              plt.subplot(2, 2, 1)
              plt.plot(range(1, len(self.dd_track_city) + 1), self.dd_track_city)
              plt.title('Demand towards City')
              plt.xlabel('Iteration'); plt.ylabel('Demand')
              plt.subplot(2, 2, 2)
              plt.plot(range(1, len(self.back_log_track_city) + 1), self.back_log_track_city)
              plt.title('Back log towards City')
              plt.xlabel('Iteration'); plt.ylabel('Back Log Count')
              plt.subplot(2, 2, 3)
              plt.plot(range(1, len(self.dd_track_tuas) + 1), self.dd_track_tuas)
              plt.title('Demand towards Tuas')
              plt.xlabel('Iteration'); plt.ylabel('Demand')
              plt.subplot(2, 2, 4)
              plt.plot(range(1, len(self.back_log_track_tuas) + 1), self.back_log_track_tuas)
              plt.title('Back log towards Tuas')
              plt.xlabel('Iteration'); plt.ylabel('Back Log Count')
              plt.subplots_adjust(hspace = 0.8, wspace = 0.8)
              plt.savefig('Demand And Backlog.png')
              plt.show()
              
              print('\nDemand Stats:', '\n###TO CITY###', '\nAvg:\t', round(np.mean(self.dd_track_city), 2), '\nMax:\t', max(self.dd_track_city), '\n###TO TUAS###', '\nAvg:\t', round(np.mean(self.dd_track_tuas), 2), '\nMax:\t', max(self.dd_track_tuas))
              print('\nBack Log Stats:', '\n###TO CITY###', '\nAvg:\t', round(np.mean(self.back_log_track_city), 2), '\nMax:\t', max(self.back_log_track_city), '\n###TO TUAS###', '\nAvg:\t', round(np.mean(self.back_log_track_tuas), 2), '\nMax:\t', max(self.back_log_track_tuas))
              
              text_file = open('Demand And Backlog.txt', 'w')
              text_file.writelines(['Demand Stats:', 
                                    '\n###TO CITY###', 
                                    '\nAvg:\t' + str(round(np.mean(self.dd_track_city), 2)), 
                                    '\nMax:\t' + str(max(self.dd_track_city)), 
                                    '\n###TO TUAS###', 
                                    '\nAvg:\t' + str(round(np.mean(self.dd_track_tuas), 2)),
                                    '\nMax:\t' + str(max(self.dd_track_tuas)),
                                    '\n\nBack Log Stats:', 
                                    '\n###TO CITY###', 
                                    '\nAvg:\t' + str(round(np.mean(self.back_log_track_city), 2)),
                                    '\nMax:\t' + str(max(self.back_log_track_city)),
                                    '\n###TO TUAS###',
                                    '\nAvg:\t' + str(round(np.mean(self.back_log_track_tuas), 2)),
                                    '\nMax:\t' + str(max(self.back_log_track_tuas))])
              text_file.close()
              os.chdir(origin)
               
       def plot(self):
              """
              function:     to plot out all the evaluation models and export all the plots and evaluations
              input:        None
              returns:      text and png files alongside the plots in the console
              """
              # vehicle location trends
              self.plot_vehicle_pattern()
              
              # diagnostics for loads that were carried
              self.plot_varying_loads()
              
              # text for load evaluation
              self.load_evaluation()
              
              # backlog and demand diagnostics
              self.plot_dd_back_log()
              
              # how many containers have been moved
              total_containers = len(self.container['moved_index']) - self.container['moved_index'].count('init') - self.container['moved_index'].count('hs')
              moved_1s = self.container['moved_index'].count(1)
              not_moved_0s = self.container['moved_index'].count(0)
              couldnt_move_n2 = self.container['moved_index'].count('N2')
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
              
       ##################### ACTUAL SIMULATION #########################
       def simulate_shifting(self, df, n = 1000, headspace = 50, bl = 100, init = 50):
              """
              function:     simulates the shifting of containers between tuas and city
              input:        scenario data in the form of a dataframe with only the number of containers that it wants to simulate,
                            the number of scenario it wants to simulate,
                            the amount of headspace given to run,
                            the amount of backlog,
                            the amount to use for initialisation (something like a seed)
              returns:      DataFrame [Refer to export_result() function to find out what's being exported] and Plots
       
              Goal:  I'd say it's to minimize the number of half and empty loads
                     while trying to maximize full loads.
       
              """
              # creating the headspace in the dataset
              if headspace != 0:
                     print('Invalid Dataset Format: Dataset requires resolving!\n')
                     print('Resolving dataset...')
                     last_date = df.iat[n - 1, 3]
                     def add_headspace(multiple, date):
                            return pd.DataFrame([[-1, 'Neither', 0, date + datetime.timedelta(minutes = 5.0 * multiple), -1]], 
                                                columns = ['index', 'DIRECTION_shift', 'LEN_Q', 'DISC_DT', 'Connect_SceneC'])
                     for i in range(1, headspace + 1):
                            df = df.append(add_headspace(i, last_date))
                     print('Resolved!\n')

              print('Commencement of Simulation with parameters:\n', 
                    str(n) + ' Observations with ' + str(headspace) + ' headspace,\n', 
                    str(bl) + ' Back-log, and\n', 
                    str(init) + ' for Initialisation')
              
              # this is to record the movements of the containers
              self.container['moved_index'] = [0]*n + ['hs']*headspace
              self.container['time']['depart'] = [0]*n + ['hs']*headspace
              self.container['time']['arrive'] = [0]*n + ['hs']*headspace
              self.container['excess'] = ['0']*n + ['hs']*headspace
       
              for i in range(bl, n + headspace):
                     # terminate if all containers have been moved
                     if 0 not in self.container['moved_index']:
                            break
                     
                     # this is to 'naturally' initialize the variables
                     if i == init + bl:
                            # containers that have made the full trip are considered used for initialisation. those that are not will be in transit or considered backlog
                            container_bool = np.where(np.asarray(self.container['time']['arrive'][:init + bl + 1]) == 0, False, True)
                            for i, b in enumerate(container_bool):
                                   if b:
                                          self.container['moved_index'][i], self.container['time']['depart'][i], self.container['time']['arrive'][i], self.container['excess'][i] = 'init', 'init', 'init', 'init'
       
                            # restarting the tracking of PMs at Tuas, City and Transit
                            temp = self.transit_track.pop()
                            self.transit_track.clear()   
                            self.transit_track.append(temp)
                            temp = self.tuas_track.pop()
                            self.tuas_track.clear()
                            self.tuas_track.append(temp)
                            temp = self.city_track.pop()
                            self.city_track.clear()
                            self.city_track.append(temp)
       
                            self.full_load = 0
                            self.half_load = 0
                            self.empty_load = 0
       
                     # tracking the counts at each location
                     self.tuas_track.append(self.PMs_track['tuas'])
                     self.city_track.append(self.PMs_track['city'])
                     self.transit_track.append(len(self.PMs_track['transit']['time']))
       
                     # structure observation data
                     going_to, container_size, disc_dt, connect_time = df.iat[i, 1], df.iat[i, 2], df.iat[i, 3], df.iat[i, 4] 
       
                     # update the PMs that are on transit, to check if they've reached the other location
                     transit = self.PMs_track['transit']
                     if transit['time']:
                            # declaring the rest of the variables
                            transit_time, transit_dest, transit_index, transit_size = transit['time'], transit['dest'], transit['index'], transit['size']
                            
                            # getting the duration each PM has been on transit for
                            trans_updater = [self.get_hours(disc_dt - x) for x in transit_time] # changed
                            # the function returns a boolean list of the PMs that have returned or not
                            trans_updater = self.pm_arrival_updater(trans_updater, transit_size, transit_time)
                            
                            # update the venues and container
                            finished_pm_index = [a for a, b in enumerate(trans_updater) if b == False]
                            for index in finished_pm_index:
                                   # update location count
                                   self.PMs_track[transit_dest[index]] += 1
                                   
                                   # update PMs
                                   arrived_pm = [x for x in self.PMs.values() if transit_index[index] in x.work_log['container']][0] # changed
                                   arrived_pm.location, arrived_pm.current_dest = arrived_pm.current_dest, None
                                   
                                   arrived_pm.work_log['arrive'] += [disc_dt]
       
                                   # update containers
                                   if type(transit_index[index]) != str:
                                          if type(transit_index[index]) == list:
                                                 arrival_index_1, arrival_index_2 = transit_index[index]
                                                 self.container['time']['arrive'][arrival_index_1] = disc_dt
                                                 self.container['excess'][arrival_index_1] = df.iat[arrival_index_1, 4] - self.get_hours(disc_dt - self.container['time']['depart'][arrival_index_1] - datetime.timedelta(minutes = 15))
       
                                                 self.container['time']['arrive'][arrival_index_2] = disc_dt
                                                 self.container['excess'][arrival_index_2] = df.iat[arrival_index_2, 4] - self.get_hours(disc_dt - self.container['time']['depart'][arrival_index_2] - datetime.timedelta(minutes = 15))
                                          else:
                                                 arrival_index = transit_index[index]
                                                 self.container['time']['arrive'][arrival_index] = disc_dt
                                                 self.container['excess'][arrival_index] = df.iat[arrival_index, 4] - self.get_hours(disc_dt - self.container['time']['depart'][arrival_index] - datetime.timedelta(minutes = 15))
                            
                            self.PMs_track['transit']['time'] = list(compress(transit_time, trans_updater))
                            self.PMs_track['transit']['dest'] = list(compress(transit_dest, trans_updater))
                            self.PMs_track['transit']['index'] = list(compress(transit_index, trans_updater))
                            self.PMs_track['transit']['size'] = list(compress(transit_size, trans_updater))
       
                     # checking of demand and backlog
                     # look before
                     back_log_to_city = sum(df.iloc[[ind for ind, stat in enumerate(self.container['moved_index'][:i]) if stat == 0], 1] == 'EB_City')
                     back_log_to_tuas = sum(df.iloc[[ind for ind, stat in enumerate(self.container['moved_index'][:i]) if stat == 0], 1] == 'WB_Tuas')
                     # look after
                     dd_to_tuas, dd_to_city = 0, 0
                     dd_present_time, dd_advance_time = disc_dt, disc_dt
                     count = i + 1
                     while count < n - 1 and self.get_hours(dd_advance_time - dd_present_time) <= self.forward_dd:
                            if df.iat[count, 1] == 'EB_City':
                                   dd_to_city += 1
                            else:
                                   dd_to_tuas += 1
                            count += 1
                            dd_advance_time = df.iat[count, 3]
                     self.back_log_track_city.append(back_log_to_city)
                     self.back_log_track_tuas.append(back_log_to_tuas)
                     self.dd_track_city.append(dd_to_city)
                     self.dd_track_tuas.append(dd_to_tuas)
       
                     # checking on the number of PMs otw to each location
                     transit_to_dest = self.get_transit_dest_count()
                     transit_to_city, transit_to_tuas = transit_to_dest['city'], transit_to_dest['tuas']
       
                     # updating of unmoved containers
                     if 0 in self.container['moved_index'][:i]:
                            # look for the indexes of the containers that haven't been moved
                            index_zero = [ind for ind, e in enumerate(self.container['moved_index'][:i]) if e == 0]
                            # sort based on connection time (shortest to longest)
                            index_zero.sort(key = lambda x: df.iat[x, 4] - self.get_hours(disc_dt - df.iat[x, 3]))
                            # based on the container indexes, i look up its information based on the dataframe
                            for j in index_zero:
                                   # will settle the container that has the shortest connection time remaining (from the current time of pm activation to load_dt)       
                                   zero_going_to, zero_container_size, zero_disc_dt, zero_connect_time = df.iat[j, 1], df.iat[j, 2], df.iat[j, 3], df.iat[j, 4]
                                   # while updating the connection time based on when it arrived to the port till the time we can activate a PM to send it
                                   zero_connect_time = zero_connect_time - self.get_hours(disc_dt - zero_disc_dt)
                                   if zero_container_size >= 22:
                                          zero_container_size = 'full'
                                   else:
                                          zero_container_size = 'half'
       
                                   # if it's a full load or there's not much time left, we just activate an available PM (if there are any) to send it over
                                   if zero_connect_time < self.threshold_connectingtime or zero_container_size == 'full':
                                          if zero_going_to == 'EB_City':
                                                 # get a PM
                                                 duty_pm = self.check_pm_avail(disc_dt, 'city', zero_container_size)
                                                 if self.PMs_track['tuas'] > 0 and duty_pm:
                                                        # update duty_pm
                                                        duty_pm.location = 'transit'
                                                        duty_pm.current_dest = 'city'
                                                        duty_pm.trips_count[zero_container_size] += 1
                                                        duty_pm.trips_count['dest'] += ['city']
                                                        duty_pm.work_log['depart'] += [disc_dt]
                                                        duty_pm.work_log['container'] += [j]
       
                                                        self.PMs_track['tuas'] -= 1
       
                                                        self.PMs_track['transit']['time'] += [disc_dt]
                                                        self.PMs_track['transit']['dest'] += ['city']
                                                        self.PMs_track['transit']['index'] += [j]
                                                        self.PMs_track['transit']['size'] += [zero_container_size]

                                                        # if we missed it, we mark as N2
                                                        if zero_connect_time <= self.travel_duration(zero_container_size, disc_dt):
                                                               self.container['moved_index'][j] = 'N2'
                                                        else:
                                                               self.container['moved_index'][j] = 1
                                                        self.container['time']['depart'][j] = disc_dt + datetime.timedelta(minutes = 15)
                                                        if zero_container_size == 'full':
                                                               self.full_load += 1
                                                        else:
                                                               self.half_load += 1
                                          # going tuas
                                          else:
                                                 # get a PM
                                                 duty_pm = self.check_pm_avail(disc_dt, 'tuas', zero_container_size)
                                                 if self.PMs_track['city'] > 0 and duty_pm:
                                                        # update duty_pm
                                                        duty_pm.location = 'transit'
                                                        duty_pm.current_dest = 'tuas'
                                                        duty_pm.trips_count[zero_container_size] += 1
                                                        duty_pm.trips_count['dest'] += ['tuas']
                                                        duty_pm.work_log['depart'] += [disc_dt]
                                                        duty_pm.work_log['container'] += [j]
       
                                                        self.PMs_track['city'] -= 1
       
                                                        self.PMs_track['transit']['time'] += [disc_dt]
                                                        self.PMs_track['transit']['dest'] += ['tuas']
                                                        self.PMs_track['transit']['index'] += [j]
                                                        self.PMs_track['transit']['size'] += [zero_container_size]
       
                                                        # if we missed it, we mark as N2
                                                        if zero_connect_time <= self.travel_duration(zero_container_size, disc_dt):
                                                               self.container['moved_index'][j] = 'N2'
                                                        else:
                                                               self.container['moved_index'][j] = 1
                                                        self.container['time']['depart'][j] = disc_dt + datetime.timedelta(minutes = 15)
                                                        if zero_container_size == 'full':
                                                               self.full_load += 1
                                                        else:
                                                               self.half_load += 1
                                   
                                   # no point settling backlog if there're no more available PMs on either side
                                   if self.PMs_track['city'] + self.PMs_track['tuas'] == 0:
                                          break
                                   
                            # check if there're still unmoved containers after moving the urgent and full loads
                            # send the half loads as full loads
                            if 0 in self.container['moved_index'][:i] and (self.PMs_track['city'] + self.PMs_track['tuas'] != 0):
                                   index_zero = [ind for ind, e in enumerate(self.container['moved_index'][:i]) if e == 0]
                                   # only handling half containers
                                   index_zero = [x for x in index_zero if df.iat[x, 2] == 20]
                                   
                                   index_zero_to_tuas = [x for x in index_zero if df.iat[x, 1] == 'WB_Tuas'] 
                                   
                                   # sort by connection time remaining (shortest to longest)
                                   index_zero_to_tuas.sort(key = lambda x: df.iat[x, 4] - self.get_hours(disc_dt - df.iat[x, 3])) 
                                   
                                   index_zero_to_city = [x for x in index_zero if df.iat[x, 1] == 'EB_City']
                                   # sort by connection time remaining (shortest to longest)
                                   index_zero_to_city.sort(key = lambda x: df.iat[x, 4] - self.get_hours(disc_dt - df.iat[x, 3])) 
                                   
                                   if index_zero_to_tuas:
                                          for j in range(1, len(index_zero_to_tuas), 2):
                                                 h = index_zero_to_tuas[j]
                                                 h_index = index_zero_to_tuas[j - 1]
                                                 
                                                 duty_pm = self.check_pm_avail(disc_dt, 'tuas', 'full')
                                                 if self.PMs_track['city'] > 0 and duty_pm:
                                                        # update duty_pm
                                                        duty_pm.location = 'transit'
                                                        duty_pm.current_dest = 'tuas'
                                                        duty_pm.trips_count['full'] += 1
                                                        duty_pm.trips_count['dest'] += ['tuas']
                                                        duty_pm.work_log['depart'] += [disc_dt]
                                                        duty_pm.work_log['container'] += [[h, h_index]]
       
                                                        self.PMs_track['city'] -= 1
       
                                                        self.PMs_track['transit']['time'] += [disc_dt]
                                                        self.PMs_track['transit']['dest'] += ['tuas']
                                                        self.PMs_track['transit']['index'] += [[h, h_index]]
                                                        self.PMs_track['transit']['size'] += ['full']
       
                                                        self.container['moved_index'][h] = 1
                                                        self.container['moved_index'][h_index] = 1
                                                        self.container['time']['depart'][h] = disc_dt + datetime.timedelta(minutes = 15)
                                                        self.container['time']['depart'][h_index] = disc_dt + datetime.timedelta(minutes = 15)
       
                                                        self.full_load += 1
                                                 
                                                 # if there're no more PMs available at city, just break the loop
                                                 if self.PMs_track['city'] == 0:
                                                        break
                                          
                                   if index_zero_to_city:
                                          for j in range(1, len(index_zero_to_city), 2):
                                                 h = index_zero_to_city[j]
                                                 h_index = index_zero_to_city[j - 1]
                                                 
                                                 duty_pm = self.check_pm_avail(disc_dt, 'city', 'full')
                                                 if self.PMs_track['tuas'] > 0 and duty_pm:
                                                        # update duty_pm
                                                        duty_pm.location = 'transit'
                                                        duty_pm.current_dest = 'city'
                                                        duty_pm.trips_count['full'] += 1
                                                        duty_pm.trips_count['dest'] += ['city']
                                                        duty_pm.work_log['depart'] += [disc_dt]
                                                        duty_pm.work_log['container'] += [[h, h_index]]
                                                        
                                                        self.PMs_track['tuas'] -= 1
                                                        
                                                        self.PMs_track['transit']['time'] += [disc_dt]
                                                        self.PMs_track['transit']['dest'] += ['city']
                                                        self.PMs_track['transit']['index'] += [[h, h_index]]
                                                        self.PMs_track['transit']['size'] += ['full']
                                                        
                                                        self.container['moved_index'][h] = 1
                                                        self.container['moved_index'][h_index] = 1
                                                        self.container['time']['depart'][h] = disc_dt + datetime.timedelta(minutes = 15)
                                                        self.container['time']['depart'][h_index] = disc_dt + datetime.timedelta(minutes = 15)
       
                                                        self.full_load += 1
                                                        
                                                 # if there're no more PMs available at tuas, just break the loop
                                                 if self.PMs_track['tuas'] == 0:
                                                        break
       
                     # for full length containers
                     if container_size > 22:
                            # initiate PM
                            if going_to == 'EB_City':
                                   # get a PM
                                   duty_pm = self.check_pm_avail(disc_dt, 'city', 'full')
                                   if self.PMs_track['tuas'] > 0 and duty_pm:
                                          # update duty_pm
                                          duty_pm.location = 'transit'
                                          duty_pm.current_dest = 'city'
                                          duty_pm.trips_count['full'] += 1
                                          duty_pm.trips_count['dest'] += ['city']
                                          duty_pm.work_log['depart'] += [disc_dt]
                                          duty_pm.work_log['container'] += [i]
       
                                          self.PMs_track['tuas'] -= 1
       
                                          self.PMs_track['transit']['time'] += [disc_dt]
                                          self.PMs_track['transit']['dest'] += ['city']
                                          self.PMs_track['transit']['index'] += [i]
                                          self.PMs_track['transit']['size'] += ['full']
       
                                          self.container['moved_index'][i] = 1
                                          self.container['time']['depart'][i] = disc_dt + datetime.timedelta(minutes = 15)
       
                                          self.full_load += 1
                            else:
                                   # get a PM
                                   duty_pm = self.check_pm_avail(disc_dt, 'tuas', 'full')
                                   if self.PMs_track['city'] > 0 and duty_pm:
                                          # update duty_pm
                                          duty_pm.location = 'transit'
                                          duty_pm.current_dest = 'tuas'
                                          duty_pm.trips_count['full'] += 1
                                          duty_pm.trips_count['dest'] += ['tuas']
                                          duty_pm.work_log['depart'] += [disc_dt]
                                          duty_pm.work_log['container'] += [i]
       
                                          self.PMs_track['city'] -= 1
       
                                          self.PMs_track['transit']['time'] += [disc_dt]
                                          self.PMs_track['transit']['dest'] += ['tuas']
                                          self.PMs_track['transit']['index'] += [i]
                                          self.PMs_track['transit']['size'] += ['full']
       
                                          self.container['moved_index'][i] = 1
                                          self.container['time']['depart'][i] = disc_dt + datetime.timedelta(minutes = 15)
       
                                          self.full_load += 1
       
                     # for half length containers
                     elif container_size > 0:
                            # finding other half loads that are available
                            index, index_going_to, index_container_size = None, None, None
                            if 0 in self.container['moved_index'][:i]:
                                   # search for the first 0 then start from there. so we slice from [first zero index:i] (can be O(logn))
                                   # settling any prior container of size 20 that's yet to be shipped
                                   index_twenties = [j for j, e in enumerate(self.container['moved_index'][:i]) if e == 0]
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
                                          duty_pm = self.check_pm_avail(disc_dt, 'city', 'full')
                                          if self.PMs_track['tuas'] > 0 and duty_pm:
                                                 # update duty_pm
                                                 duty_pm.location = 'transit'
                                                 duty_pm.current_dest = 'city'
                                                 duty_pm.trips_count['full'] += 1
                                                 duty_pm.trips_count['dest'] += ['city']
                                                 duty_pm.work_log['depart'] += [disc_dt]
                                                 duty_pm.work_log['container'] += [[i, index]]
       
                                                 self.PMs_track['tuas'] -= 1
       
                                                 self.PMs_track['transit']['time'] += [disc_dt]
                                                 self.PMs_track['transit']['dest'] += ['city']
                                                 self.PMs_track['transit']['index'] += [[i, index]]
                                                 self.PMs_track['transit']['size'] += ['full']
       
                                                 self.container['moved_index'][i] = 1
                                                 self.container['moved_index'][index] = 1
                                                 self.container['time']['depart'][i] = disc_dt + datetime.timedelta(minutes = 15)
                                                 self.container['time']['depart'][index] = disc_dt + datetime.timedelta(minutes = 15)
       
                                                 self.full_load += 1
                                   else:
                                          # get a PM
                                          duty_pm = self.check_pm_avail(disc_dt, 'tuas', 'full')
                                          if self.PMs_track['city'] > 0 and duty_pm:
                                                 duty_pm.location = 'transit'
                                                 duty_pm.current_dest = 'tuas'
                                                 duty_pm.trips_count['full'] += 1
                                                 duty_pm.trips_count['dest'] += ['tuas']
                                                 duty_pm.work_log['depart'] += [disc_dt]
                                                 duty_pm.work_log['container'] += [[i, index]]
       
                                                 self.PMs_track['city'] -= 1
       
                                                 self.PMs_track['transit']['time'] += [disc_dt]
                                                 self.PMs_track['transit']['dest'] += ['tuas']
                                                 self.PMs_track['transit']['index'] += [[i, index]]
                                                 self.PMs_track['transit']['size'] += ['full']
       
                                                 self.container['moved_index'][i] = 1
                                                 self.container['moved_index'][index] = 1
                                                 self.container['time']['depart'][i] = disc_dt + datetime.timedelta(minutes = 15)
                                                 self.container['time']['depart'][index] = disc_dt + datetime.timedelta(minutes = 15)
       
                                                 self.full_load += 1
       
                            # if there're no other half loads available
                            else:
                                   if going_to == 'EB_City':
                                          # 1. too little PMs on the other side, 2. connection time is low, 3. demand towards where it's leaving from is high
                                          if (self.PMs_track[going_to[3:].lower()] < self.threshold_vehicle_half and dd_to_tuas > self.threshold_dd) or connect_time < self.threshold_connectingtime: 
                                                 # get a PM
                                                 duty_pm = self.check_pm_avail(disc_dt, 'city', 'half')
                                                 if self.PMs_track['tuas'] > 0 and duty_pm:
                                                        # update duty_pm
                                                        duty_pm.location = 'transit'
                                                        duty_pm.current_dest = 'city'
                                                        duty_pm.trips_count['half'] += 1
                                                        duty_pm.trips_count['dest'] += ['city']
                                                        duty_pm.work_log['depart'] += [disc_dt]
                                                        duty_pm.work_log['container'] += [i]
       
                                                        self.PMs_track['tuas'] -= 1
       
                                                        self.PMs_track['transit']['time'] += [disc_dt]
                                                        self.PMs_track['transit']['dest'] += ['city']
                                                        self.PMs_track['transit']['index'] += [i]
                                                        self.PMs_track['transit']['size'] += ['half']
       
                                                        self.container['moved_index'][i] = 1
                                                        self.container['time']['depart'][i] = disc_dt + datetime.timedelta(minutes = 15)
                                                        self.half_load += 1
                                   else:
                                          if (self.PMs_track[going_to[3:].lower()] < self.threshold_vehicle_half and dd_to_city > self.threshold_dd) or connect_time < self.threshold_connectingtime:
                                                 # get a PM
                                                 duty_pm = self.check_pm_avail(disc_dt, 'tuas', 'half')
                                                 if self.PMs_track['city'] > 0 and duty_pm:
                                                        # update duty_pm
                                                        duty_pm.location = 'transit'
                                                        duty_pm.current_dest = 'tuas'
                                                        duty_pm.trips_count['half'] += 1
                                                        duty_pm.trips_count['dest'] += ['tuas']
                                                        duty_pm.work_log['depart'] += [disc_dt]
                                                        duty_pm.work_log['container'] += [i]
       
                                                        self.PMs_track['city'] -= 1
       
                                                        self.PMs_track['transit']['time'] += [disc_dt]
                                                        self.PMs_track['transit']['dest'] += ['tuas']
                                                        self.PMs_track['transit']['index'] += [i]
                                                        self.PMs_track['transit']['size'] += ['half']
       
                                                        self.container['moved_index'][i] = 1
                                                        self.container['time']['depart'][i] = disc_dt + datetime.timedelta(minutes = 15)
                                                        self.half_load += 1
       
                     # sending empty PMs to city
                     if (dd_to_tuas > self.threshold_dd_empty or back_log_to_tuas > self.threshold_back_log) and (self.PMs_track['city'] + transit_to_city <= self.threshold_empty_movement):
                            if self.PMs_track['tuas'] >= self.threshold_vehicle_half:
                                   for p in range(self.move_over):
                                          # get a PM
                                          duty_pm = self.check_pm_avail(disc_dt, 'city', 'empty')
                                          if duty_pm:
                                                 # update duty_pm
                                                 duty_pm.location = 'transit'
                                                 duty_pm.current_dest = 'city'
                                                 duty_pm.trips_count['empty'] += 1
                                                 duty_pm.trips_count['dest'] += ['city']
                                                 duty_pm.work_log['depart'] += [disc_dt]
                                                 duty_pm.work_log['container'] += ['empty' + str(p) + '|' + str(i)]
       
                                                 self.PMs_track['tuas'] -= 1
       
                                                 self.PMs_track['transit']['time'] += [disc_dt]
                                                 self.PMs_track['transit']['dest'] += ['city']
                                                 self.PMs_track['transit']['index'] += ['empty' + str(p) + '|' + str(i)]
                                                 self.PMs_track['transit']['size'] += ['empty']
       
                                                 self.empty_load += self.move_over
                     
                     # sending empty PMs to tuas
                     if (dd_to_city > self.threshold_dd_empty or back_log_to_city > self.threshold_back_log) and (self.PMs_track['tuas'] + transit_to_tuas <= self.threshold_empty_movement):
                            if self.PMs_track['city'] >= self.threshold_vehicle_half:
                                   for p in range(self.move_over):
                                          # get a PM
                                          duty_pm = self.check_pm_avail(disc_dt, 'tuas', 'empty')
                                          if duty_pm:
                                                 # update duty_pm
                                                 duty_pm.location = 'transit'
                                                 duty_pm.current_dest = 'tuas'
                                                 duty_pm.trips_count['empty'] += 1
                                                 duty_pm.trips_count['dest'] += ['tuas']
                                                 duty_pm.work_log['depart'] += [disc_dt]
                                                 duty_pm.work_log['container'] += ['empty' + str(i) + '|' + str(p)]
       
                                                 self.PMs_track['city'] -= 1
       
                                                 self.PMs_track['transit']['time'] += [disc_dt]
                                                 self.PMs_track['transit']['dest'] += ['city']
                                                 self.PMs_track['transit']['index'] += ['empty' + str(i) + '|' + str(p)]
                                                 self.PMs_track['transit']['size'] += ['empty']
       
                                                 self.empty_load += self.move_over
                     # Loading Bar
                     stop_values = list(map(lambda x: floor(x), np.linspace(bl, n - 1, 11)))
                     if i in stop_values:
                            prop_done = stop_values.index(i)
                            print('[' + '###'*prop_done + '   '*(10 - prop_done) + ']' + '  ' + str(prop_done*10) + '% done')
              
              # to export a .csv file
              print('\nSimulation Complete!')
              print('Exporting Results and Plotting Evaluation...')
              self.export_result()
              self.plot()                                                                       
