"""test1.py
    Created by Aaron at 27-May-20"""
import pprint
import numpy
import pandas as pd

# all possible timeslot
default_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
all_timeslot = [x for x in range(1,301)]

# read HC03.csv for venue unavailability
df = pd.read_csv('HC03.csv', sep=',', header=None)
unavailable_timeslot = numpy.array(df)

# remove other non-data
unavailable_timeslot = [y for x in unavailable_timeslot for y in set(x) if str(y).isnumeric()]
# remove unavailable timeslot from all timeslot to obtain only possible timeslot
for x in unavailable_timeslot:
    all_timeslot.remove(x)
# print(all_timeslot)

# read SupExaAssign.csv for presentaion group
df = pd.read_csv('SupExaAssign.csv', sep=',')
SupExaAssign = numpy.matrix(df)
print(SupExaAssign)

Models

# SupExaAssign -> staff_unavailability -> compute all possible time for them -> (all-timeslot - staff_unavailability)