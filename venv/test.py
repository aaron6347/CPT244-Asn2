"""test.py
    Created by Aaron at 11-Jun-20"""
import random
ranslots = list(range(1, 300))
random.shuffle(ranslots)
print(ranslots)
x = 10
a = 0 if x == 0 else 1
print(a)

a=[(1,1),(2,0)]
print(min(a, key=lambda tup: tup[1]))

a = random.choice((0,1))
for x in range(10):
    print(random.choice((0, 1)))

# a = 0
# while a < 10:
#     if random.uniform(0, 1) > 0.5:
#         aa = 10
#         aa += 1
#     if random.uniform(0, 1) > 0.1:
#         ya = aa
#         print(ya, aa)
#     aa = None
#     a += 1

a = [1, 16, 31, 2, 3, 18]
a = [x%15 for x in a]
import collections
x = collections.Counter(a)
print(x)

score = 0
a = {1: [181, 10, 236, 164, 53, 65, 281, 102], 2: [], 3: [181, 21, 115, 69, 229, 242, 53, 59, 65, 281, 244], 4: [1, 17, 33, 49, 65, 81, 82, 98, 114, 130, 146]}
for _, timeslot in a.items():  # traverse and check each staff
    checked = []    #to store time that has been checked
    print(_, timeslot, score)
    for each in timeslot:   #traverse and check each timeslot
        if each not in checked: #if the timeslot hasn't been check yet
            n = 0   #increment for 16 to find consecutive presentation
            while True:
                time = each + (16 * n)  #expected next consecutive timeslot
                if time in timeslot:    #if next consecutive timeslot exist in timeslot then record as checked
                    checked.append(time)
                    if n > 3:   #if the consecutive has been more than 4 times then give penalty
                        score += 10
                else:
                    break
                n += 1
print(score)
import csv

# with open('data/HC03.csv', 'r') as file:
#     reader = csv.reader(file)
#     for row in reader:
#         print(row)
#         aaa = [x for x in set(row) if str(x).isnumeric()]
# print(aaa)

# with open('data/HC04.csv', 'r') as file:
#     reader = csv.reader(file)
#     unavailable_staff2 = [[int(x) for x in row if str(x).isnumeric()] for row in reader]
# print(unavailable_staff2)

# with open('data/SC03.csv', 'r') as file:
#     reader = csv.reader(file)
#     sc03_csv = [pref for _, pref in reader]
# print(sc03_csv)

# with open('data/SupExaAssign.csv', 'r') as file:
#     reader = csv.reader(file)
#     next(reader)
#     for row in reader:
#         print(row)

# with open('data/HC03.csv', 'r') as file:
#     reader = csv.reader(file)
#     unavailable_timeslot = [[x for x in set(row) if str(x).isnumeric()] for row in reader]
# print(unavailable_timeslot)


score = 0
found = []

for _, timeslot in {"a": [1, 16, 31, 46, 76, 61], "b": [2, 18, 33, 3, 62, 47, 15, ]}.items():  #traverse and check each staff
    checked = []
    for each in timeslot:
        if each not in checked:
            primary = each % 15
            if primary == 0:
                primary = 15
            base = int(each / 61)
            same_time = [primary + 60 * base + 15 * x for x in range(4)]
            for finding in same_time:
                if finding in timeslot and finding != each and finding not in checked:
                    found.append(finding)
                    score += 1000
                checked.append(finding)
# print(score)
# print(found)
print('--------------')
score = 0
for _, timeslot in {"a": [1, 20, 16, 31, 46, 76, 61, 32, 3, 13, 12, 14, 15, 9, 10, 11], "b": [2, 18, 33, 3, 62, 47, 15]}.items():  # traverse and check each staff
    checked = []  # to store time that has been checked
    for each in sorted(timeslot):  # traverse and check each timeslot
        if each not in checked:  # if the timeslot hasn't been check yet
            checked.append(each)
            primary = each % 15
            if primary == 0:
                primary = 15
            if primary >= 12:   #starting from 12th time period, there wont be breaking the staff preference limit
                continue
            base = each // 61
            n = 1  # increment for 16 to find consecutive presentation
            while True:
                next_time = [primary + n + 60 * base + 15 * x for x in range(4)]    #all possible next consecutive presentation timeslot
                if any(time in timeslot and time not in checked for time in next_time): #if any next consecutive timeslot exist in staff's schedule
                    checked += next_time
                    if n > 3:   #if the consecutive has reach more than staff's preference in number of consecutive presentation
                        score += 10
                    if primary + n + 60 * base == 15:   #if the consecutive has reach end of day time period
                        break
                    else:
                        n += 1  # increment n to look for next consecutive presentation timeslot
                else:   #if none next consecutive timeslot exist in staff's schedule then drop the consecutive count
                    break


# read HC03.csv for venue unavailability
unavailable_timeslot = []
with open('data/HC03.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        for x in set(row):
            if str(x).isnumeric():
                unavailable_timeslot.append(x)
print(unavailable_timeslot)