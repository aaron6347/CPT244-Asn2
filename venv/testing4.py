"""testing3.py
    Created by Aaron at 11-Jun-20"""
import csv
import pprint
import random
from Models import *
import collections

# Mapping of codes to numbers for easy processing
staff_code_to_num = {"S{:03d}".format(i + 1): i + 1 for i in range(47)}
room_code_to_num = {"VR": 1, "MR": 2, "IR": 3, "BJIM": 4}
presentation_code_to_num = {"P{}".format(i + 1): i + 1 for i in range(118)}

# extraction of assignment of staff to presentation
with open('data/SupExaAssign.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    SupExaAssign = [row for row in reader]

# storing presentation information in data model
staff_to_presentation = Presentation.presentation = [Presentation(presentation_code_to_num[j[0]],
                                                                  [staff_code_to_num[j[1]], staff_code_to_num[j[2]],
                                                                   staff_code_to_num[j[3]]]) for j in SupExaAssign]

# read HC03.csv for venue unavailability
with open('data/HC03.csv', 'r') as file:
    reader = csv.reader(file)
    unavailable_timeslot = [[x for x in set(row) if str(x).isnumeric()] for row in reader]

# read HC04.csv for staff unavailability
with open('data/HC04.csv', 'r') as file:
    reader = csv.reader(file)
    unavailable_staff = [[int(x) for x in row if str(x).isnumeric()] for row in reader]

# read SC03.csv for change of venue
with open('data/SC03.csv', 'r') as file:
    reader = csv.reader(file)
    sc03_csv = [pref for _, pref in reader]

def initialize_population(size):
    """generate population function"""
    population = []
    for i in range(size):
        chromosome = []
        timeslot = list(range(1, 301))
        random.shuffle(timeslot)
        for x in staff_to_presentation:
            chromosome.append([x, timeslot.pop()])
        population.append(chromosome)
    return population

def hc02(staff_timeslot):
    """check staff with concurrent presentation"""
    score = 0
    for _, timeslot in staff_timeslot.items():  #traverse and check each staff
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
                        score += 1000
                    checked.append(finding)
    return score

def hc03(chromosome):
    """check selected timeslot with venue unavailability function"""
    score = 0
    for group in chromosome:    #traverse and check each chromosome
        _,timeslot = group
        if timeslot in unavailable_timeslot:    #if current selected timeslot clash with venue unavailability then give penalty
            score += 1000
    return score

def hc04(chromosome):
    """check selected timeslot with group's staffs unavailability function"""
    score = 0
    for group in chromosome:    #traverse and check each chromosome
        presentation, timeslot = group
        for staff in presentation.staff:    #traverse and check each staff of the group
            if timeslot in unavailable_staff[staff-1]:  #if current selected timeslot clash with any staff unavailability then give penalty
                score += 1000
    return score

def sc01(staff_timeslot):
    """check staff with consecutive presentation"""
    score = 0
    for _, timeslot in staff_timeslot.items():  # traverse and check each staff
        checked = []    #to store time that has been checked
        # print(_, timeslot, score)
        for each in timeslot:   #traverse and check each timeslot
            if each not in checked: #if the timeslot hasn't been check yet
                n = 0   #increment for 16 to find consecutive presentation
                while True:
                    time = each + (16 * n)  #next consecutive presentation timeslot
                    if time in timeslot:    #if next consecutive presentation timeslot exist in timeslot then record as checked
                        checked.append(time)
                        if n > 3:   #if the consecutive has been more than 4 times then give penalty
                            score += 10
                    else:   #if the next consecutive presentation timeslot doesn't exist in timeslot then break loop
                        break
                    n += 1  #increment n to look for next consecutive presentation timeslot
    return score

def sc02(staff_timeslot):
    """check staff with number of days"""
    score = 0
    for _, timeslot in staff_timeslot.items():  # traverse and check each staff
        day_counter = {'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0, 'Friday': 0}   #to store each day's presentation
        for time in timeslot:   #traverse and check each timeslot
            if 0 < time < 61:   #increment counter by distribute timeslot into corresponding days
                day_counter["Monday"] += 1
            elif 60 < time < 121:
                day_counter["Tuesday"] += 1
            elif 120 < time < 181:
                day_counter["Wednesday"] += 1
            elif 180 < time < 241:
                day_counter["Thursday"] += 1
            else:
                day_counter["Friday"] += 1
        # print(day_counter)
        for _ in range(2):  #find the 2 lowest presentation days to use as penalty
            min_val = min(day_counter.values())
            min_day = min(day_counter.keys(), key=lambda x: day_counter[x])
            score += min_val * 10   #2 lowest presentation days counter value will be used as penalty
            day_counter.pop(min_day)    #pop out the lowest presentation day to find 1st and 2nd lowest
    return score

def sc03(staff_timeslot):
    """check staff with change of venue"""
    score = 0
    for staff, timeslot in staff_timeslot.items():  # traverse and check each staff
        if sc03_csv[staff-1] == 'yes':  #if the staff preference not to change
            # print(staff, timeslot, score)
            timeslot = [x % 60 for x in timeslot]   #%60 to eliminate days distribution
            venue_counter = {"VR": 0, "MR": 0, "IR": 0, "BJIM": 0}  #to store each venue's presentation
            for time in timeslot:  # traverse and check each timeslot
                if 1 <= time <= 15:  #increment counter by distribute timeslot into corresponding venue
                    venue_counter["VR"] += 1
                elif 16 <= time <= 30:
                    venue_counter["MR"] += 1
                elif 31 <= time <= 45:
                    venue_counter["IR"] += 1
                else:
                    venue_counter["BJIM"] += 1
            # print(venue_counter)
            max_venue = max(venue_counter.keys(), key=lambda x: venue_counter[x])   #find the most presentation taking place venue
            venue_counter.pop(max_venue)    #pop out the most presentation taking place venue
            score += sum(venue_counter.values()) * 10    #all presentations that is not in most presentation taking place venue will be used as penalty
    return score

def evaluate(population):
    """evaluate population function"""
    result = [] #store all chromosome's score
    for x in range(len(population)):    # traverse and check each chromosome
        # creation of new data structure to each chromosome for SCs
        staff_timeslot = {x + 1: [] for x in range(47)}  # store all timeslot according to staff
        for group in population[x]:  # traverse and check each group
            presentation, timeslot = group
            staff = presentation.staff
            for each in staff:  # traverse and check each staff
                staff_timeslot[each] = staff_timeslot[each] + [timeslot]

        #check HCs and SCs
        # print(staff_timeslot)
        score = hc02(staff_timeslot)    #check staff with concurrent presentation
        score += hc03(population[x])    #check current selected timeslot with venue unavailability
        score += hc04(population[x])    #check current selected timeslot with staff unavailability
        score += sc01(staff_timeslot)   #check staff with consecutive presentation
        score += sc02(staff_timeslot)   #check staff with number of days
        score += sc03(staff_timeslot)   #check staff with change of venue
        result.append((x+1, score))
    return result

def selection(population_score):
    """select 2 parents chromosome function"""
    selectionlist = population_score[:]    #shallow copy
    random.shuffle(selectionlist)   #shuffle the selection
    result = () #to store chosen parents chromosome
    for _ in range(2):  #2 times traverse to choose 2 parents
        c1, val1 = selectionlist.pop()  #parent chromosome 1st candidate
        c2, val2 = selectionlist.pop()  #parent chromosome 2nd candidate
        result += (c2,) if val1 > val2 else (c1,)   #make comparison between both parent chromosome candidate and choose the one with lower penalty score
    print(result)
    return result

def crossover(parent1_ind, parent2_ind, population):
    """crossover 2 parents chromosome function"""
    child1, child2 = [], []
    reservoir1, reservoir2 = [], []
    for x in range(118):
        choice = random.choice((0, 1))
        _, timeslot1 = population[parent1_ind][x]
        _, timeslot2 = population[parent2_ind][x]
        if choice:
            if timeslot2 not in child1:
                child1.append(timeslot2)
            else:
                child1.append(0)
                reservoir1.append(timeslot2)
            if timeslot1 not in child2:
                child2.append(timeslot1)
            else:
                child2.append(0)
                reservoir2.append(timeslot1)
        else:
            if timeslot1 not in child1:
                child1.append(timeslot1)
            else:
                child1.append(0)
                reservoir1.append(timeslot1)
            if timeslot2 not in child2:
                child2.append(timeslot2)
            else:
                child2.append(0)
                reservoir2.append(timeslot2)
    # print(sorted(child1))
    # print(sorted(child2))
    non_existed = [x for x in range(1, 301) if x not in set(child1+child2)]
    # print(len(non_existed), sorted(non_existed))
    for ind in range(118):
        if child1[ind] == 0:
            if len(reservoir2) != 0:
                child1[ind] = reservoir2[0]
                del reservoir2 [0]
            else:
                child1[ind] = random.choice(non_existed)
                non_existed.remove(child1[ind])
        if child2[ind] == 0:
            if len(reservoir1) != 0:
                child2[ind] = reservoir1[0]
                del reservoir1 [0]
            else:
                child2[ind] = random.choice(non_existed)
                non_existed.remove(child2[ind])

    result1, result2 = [], []
    for x in range(118):
        result1.append([population[parent1_ind][x][0], child1[x]])
        result2.append([population[parent1_ind][x][0], child2[x]])
    # print(child1)
    # print(child2)
    # print('res1', result1)
    # print('res2', result2)
    return result1, result2

def mutation(chromosome):
    """mutation 2 parents/childs chromosome function"""
    existed_timeslot = [x[1] for x in chromosome]
    randomable_timeslot = [x for x in range(1, 301) if x not in (existed_timeslot or unavailable_timeslot)]
    # print(randomable_timeslot)
    index = random.randint(0, len(chromosome) - 1)
    staff_timeslot = []
    for staff in chromosome[index][0].staff:
        staff_timeslot += unavailable_staff[staff - 1]
    # print(staff_timeslot)
    for timeslot in staff_timeslot:
        if timeslot in randomable_timeslot:
            randomable_timeslot.remove(timeslot)
    # print('after remove ', randomable_timeslot)
    chromosome[index][1] = random.choice(randomable_timeslot)

def genetic_algorithm():
    """run genetic algorithm function"""
    # initialization phase
    generation = 0  #initialize generation
    crossover_prob, mutation_prob = 0.8, 0.15       # initialize probability
    # population = initialize_population(100)       # initialize population
    population = initialize_population(300)

    # evaluation process (making the first one outside so it wont generate twice)
    population_score = evaluate(population)  # evaluate population by giving each chromosome a score
    print("original population score", population_score)

    # generation phase
    # while generation < 50:
    while generation < 20:
        accumulated_child_population = []
        while len(accumulated_child_population) < int(len(population) * (1.0 - (10 / 100))):

            # selection of parents chromosome process
            parent1_ind, parent2_ind = selection(population_score)
            parent_population = [population[parent1_ind-1], population[parent2_ind-1]]
            # print(parent_population)

            # genetic process
            child_population = parent_population    #assign parent as child
            if random.uniform(0, 1) >= crossover_prob:  #probability having crossover then crossover
                child_population = crossover(parent1_ind-1, parent2_ind-1, population)
            if random.uniform(0, 1) >= mutation_prob:   #probability having mutation then mutation happen
                mutation(child_population[0])
                mutation(child_population[1])

            # evaluation process
            parent_score = evaluate(parent_population)
            child_score = evaluate(child_population)
            print('parent', parent_score, 'child', child_score)

            if child_score[0] <= parent_score[0]:
                accumulated_child_population.append(child_population[0])
            else:
                accumulated_child_population.append(parent_population[0])

            if child_score[1] <= parent_score[1]:
                accumulated_child_population.append(child_population[1])
            else:
                accumulated_child_population.append(parent_population[1])

            # # selection process
            # better_population, better_score = parent_population, parent_score   #assign parent as the best 2 result first
            # if better_score[0][1] > better_score[1][1]:   #arrange better score in ascending order
            #     better_population = [parent_population[1], parent_population[0]]
            #     better_score = [parent_score[1], parent_score[0]]
            # for ind1, score in child_score: #traver and check each child
            #     for ind2, better in enumerate(better_score):    #traverse and check each current result
            #         _, score2 = better
            #         if score < score2:  #if child penalty score is lower than current result score then change the score
            #             better_population.insert(ind2, child_population[ind1-1])
            #             better_score.insert(ind2, (ind1, score))
            #             better_population.pop()
            #             better_score.pop()
            #             break
            # print('better', better_score)

            # # replacing population process
            # population[parent1_ind - 1] = better_population[0]
            # population[parent2_ind - 1] = better_population[1]
            # population_score = evaluate(population)
            # print('final', population_score)

        j = int(len(population) * 10 / 100)
        for i in range(j):
            accumulated_child_population.append(population[i])
        population = accumulated_child_population
        population_score = evaluate(population)

        print("Best at generation: ", generation)
        print(min(population_score, key=lambda tup: tup[1]))
        generation += 1

    print("Best score so far: ")
    print(min(population_score, key=lambda tup: tup[1]))

genetic_algorithm()
