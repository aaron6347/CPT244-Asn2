"""testing3.py
    Created by Aaron at 11-Jun-20"""
import csv
import numpy
import pandas as pd
import pprint
import random
from Models import *

# Mapping of codes to numbers for easy processing
staff_code_to_num = {"S{:03d}".format(i + 1): i + 1 for i in range(47)}
room_code_to_num = {"VR": 1, "MR": 2, "IR": 3, "BJIM": 4}
presentation_code_to_num = {"P{}".format(i + 1): i + 1 for i in range(118)}

# extraction of assignment of staff to presentation
df = pd.read_csv('data/SupExaAssign.csv', sep=',')
SupExaAssign = numpy.array(df)

# storing presentation information in data model
staff_to_presentation = Presentation.presentation = [Presentation(presentation_code_to_num[j[0]],
                                                                  [staff_code_to_num[j[1]], staff_code_to_num[j[2]],
                                                                   staff_code_to_num[j[3]]]) for j in SupExaAssign]

# read HC03.csv for venue unavailability
df = pd.read_csv('data/HC03.csv', sep=',', header=None)
unavailable_timeslot = numpy.array(df)

# remove other non-data
unavailable_timeslot = [y for x in unavailable_timeslot for y in set(x) if str(y).isnumeric()]

# read HC04.csv for staff unavailability
unavailable_staff = []
with open('data/HC04.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        unavailable_staff.append([int(x) for x in row if str(x).isnumeric()])

def initialize_population(size):
    """generate population function"""
    global staff_to_presentation, unavailable_staff, unavailable_timeslot
    population = []
    for i in range(size):
        chromosome = []
        timeslot = list(range(1, 300))
        random.shuffle(timeslot)
        for x in staff_to_presentation:
            chromosome.append([x, timeslot.pop()])
        population.append(chromosome)

    # for x,v in enumerate(population):
    #     for y,val in enumerate(v):
    #         print(x, val)

    return population

def check_venue_availability(chromosome):
    """compare selected timeslot with venue unavailability function"""
    score = 0
    for group in chromosome:    #traverse and check each chromosome
        _,timeslot = group
        if timeslot in unavailable_timeslot:    #if current selected timeslot clash with venue unavailability then give penalty
            score += 1000
    return score

def check_staff_availability(chromosome):
    """compare selected timeslot with group's staffs unavailability function"""
    score = 0
    for group in chromosome:    #traverse and check each chromosome
        presentation, timeslot = group
        for staff in presentation.staff:    #traverse and check each staff of the group
            if timeslot in unavailable_staff[staff-1]:  #if current selected timeslot clash with any staff unavailability then give penalty
                score += 1000
    return score

def evaluate(population):
    """evaluate population function"""
    result = [] #store all chromosome's score
    for x in range(len(population)):
        score = check_venue_availability(population[x]) #check current selected timeslot with venue unavailability
        # print(score)
        score += check_staff_availability(population[x])    #check current selected timeslot with staff unavailability
        result.append((x+1, score))
    return result

def selection(population_score):
    """select 2 parents chromosome function"""
    selectionlist = population_score[:]    #shallow copy
    random.shuffle(selectionlist)   #shuffle the selection
    print('selectionlist after shuffle', selectionlist)
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
    existed_timeslot = [x[1] for x in chromosome]
    randomable_timeslot = [x for x in range(1, 301) if x not in existed_timeslot]
    # print(randomable_timeslot)
    index = random.randint(0, len(chromosome) - 1)
    staff_timeslot = []
    for staff in chromosome[index][0].staff:
        staff_timeslot += unavailable_staff[staff - 1]
    # print(staff_timeslot)
    for x in staff_timeslot:
        if x in randomable_timeslot:
            randomable_timeslot.remove(x)
    # print('after remove ', randomable_timeslot)
    chromosome[index][1] = random.choice(randomable_timeslot)

def genetic_algorithm():
    """run genetic algorithm function"""
    # initialization phase
    generation = 0  #initialize generation
    crossover_prob, mutation_prob = 0.8, 0.15       # initialize probability
    # population = initialize_population(100)       # initialize population
    population = initialize_population(100)

    # generation phase
    # while generation < 50:
    while generation < 500:
        # evaluation process
        population_score = evaluate(population)  # evaluate population by giving each chromosome a score
        print("original population score", population_score)

        # selection of parents chromosome process
        parent1_ind, parent2_ind = selection(population_score)
        parent_population = [population[parent1_ind-1], population[parent2_ind-1]]
        # print(parent_population)

        # genetic process
        crossover_prob = mutation_prob = 0
        if random.uniform(0, 1) >= crossover_prob:  #probability having crossover then crossover
            child_population = crossover(parent1_ind-1, parent2_ind-1, population)
        if random.uniform(0, 1) >= mutation_prob:   #probability having mutation then mutation happen
            if not child_population:    #if crossover didnt happen before in this generation then create a child population
                child_population = parent_population
            mutation(child_population[0])
            mutation(child_population[1])

        # evaluation process
        parent_score = evaluate(parent_population)
        child_score = evaluate(child_population)

        print(parent_score)
        print(child_score)
        parent_ind = 0
        for ind, chromosome in enumerate(child_score):
            _, child_score = chromosome
            if child_score < parent_score[parent_ind][1]:
                if parent_ind:
                    population[parent2_ind-1] = child_population[ind]
                else:
                    population[parent1_ind-1] = child_population[ind]
                parent_ind += 1

        population_score = evaluate(population)
        print(population_score)

        # for child_ind, child in enumerate(child_score):  # traverse and check each child chromosome
        #     _, score = child
        #     max_ind, max_val = max(population_score, key=lambda tup: tup[1])  # find the maximum penalty score from population
        #     print('max', max_ind, max_val)
        #     if max_val > score:  # if the maximum penalty score in population is higher than child penalty score then swap the child into population
        #         print('changed')
        #         population[max_ind - 1] = child_population[child_ind]
        #         population_score[max_ind - 1] = (max_ind, child_score[child_ind][1])
        # print('new population', population_score)

        child_population = None #destroy child_population before next generation
        generation += 1
    print(min(population_score, key=lambda tup: tup[1]))
genetic_algorithm()
