import copy
import csv
import math
import numpy
import pandas as pd
import pprint
import random as rand
from Models import *
from math import ceil, log2

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
    global staff_to_presentation, unavailable_staff, unavailable_timeslot
    chromosomes = []
    for i in range(size):
        # a 3 x 118 matrix where three rows are professor list, timeslot, and room id, room id can be ignored since
        # all the rooms are defined by their number.
        chromosome = []
        ranslots = list(range(1, 300))
        rand.shuffle(ranslots)
        for present in staff_to_presentation:
            slot = ranslots.pop()
            staff_slots = []
            for staff in present.staff:
                staff_slots = staff_slots + unavailable_staff[staff - 1]
            while slot in staff_slots or slot in unavailable_timeslot:
                slot = ranslots.pop()

            chromosome.append([present, slot])
        chromosomes.append(chromosome)
    return chromosomes


def check_venue_availability(chromosomes):
    score = 0
    for chromosome in chromosomes:
        if chromosome[1] in unavailable_timeslot:
            score += 1
    return score


def check_staff_availability(chromosomes):
    score = 0
    for chromosome in chromosomes:
        for staff in chromosome[0].staff:
            if chromosome[1] in unavailable_staff[staff - 1]:
                score += 1
                break
    return score


def check_venue_conflict(chromosomes):
    score = 0
    booked_slots = [x[1] for x in chromosomes]
    if len(set(booked_slots)) < 118:
        score += 1
    return score


def evaluate(chromosomes):
    score = 0
    score = score + check_venue_availability(chromosomes)
    score = score + check_staff_availability(chromosomes)
    # score = score + check_venue_conflict(chromosomes)
    return score


def check_hc_violation(chromosome):
    return True if evaluate(chromosome) >= 1 else False

def conflict_repair(chromosome):
    booked_slots = [x[1] for x in chromosome]
    ranslots = [x for x in list(range(1, 300)) if x not in set(booked_slots)]
    oc_set = set()
    conflicted_slots = []
    for idx, val in enumerate(booked_slots):
        if val not in oc_set:
            oc_set.add(val)
        else:
            conflicted_slots.append(idx)
    rand.shuffle(ranslots)

    while len(set(booked_slots)) < 118:
        chromosome[conflicted_slots.pop()][1] = ranslots.pop()
        booked_slots = [x[1] for x in chromosome]

def tournament_selection(population):
    size = len(population)
    ranlist = list(range(1, size - 1))
    rand.shuffle(ranlist)

    c1 = population[ranlist.pop()]
    c2 = population[ranlist.pop()]
    c3 = population[ranlist.pop()]
    c4 = population[ranlist.pop()]

    if evaluate(c1) < evaluate(c2):
        w1 = c1
    else:
        w1 = c2
    if evaluate(c3) < evaluate(c4):
        w2 = c3
    else:
        w2 = c4

    return w1, w2


# Modified Combination of Row_reselect, Column_reselect
def mutate(chromosome):
    global unavailable_staff, unavailable_timeslot
    ranslots = list(range(1, 300))
    index_list = list(range(0, len(chromosome) - 1))
    rand.shuffle(ranslots)
    rand.shuffle(index_list)
    ran_slot = ranslots.pop()
    index = index_list.pop()
    staff_slots = []
    # booked_timeslots = [x[1] for x in chromosome]
    for staff in chromosome[index][0].staff:
        staff_slots = staff_slots + unavailable_staff[staff - 1]
    while ran_slot in staff_slots or ran_slot in unavailable_timeslot:
        index = index_list.pop()
        ran_slot = ranslots.pop()

    chromosome[index][1] = ran_slot
    if check_venue_conflict(chromosome):
        conflict_repair(chromosome)


def crossover(p1, p2):
    # a = random.randint(0, len(population) - 1)
    # b = random.randint(0, len(population) - 1)
    child1 = list([p1[x1] for x1 in range(len(p1) - 59)] + [p2[x2] for x2 in range(59, len(p2))])
    child2 = list([p2[x1] for x1 in range(len(p2) - 59)] + [p1[x2] for x2 in range(59, len(p1))])
    return child1, child2


def genetic_algorithm():
    generation = 0
    crossover_prob = 0.8
    mutation_prob = 0.15
    population = initialize_population(100)
    test = population[0]
    print(len(test))
    print(evaluate(test))
    print("Original population:")
    print(population)
    print("Original costs:")
    print("\n------------- Genetic Algorithm --------------\n")
    population.sort(key=evaluate)
    print(len(population))

    while generation < 50:
        child_population = []
        while len(child_population) < int(len(population) * (1.0 - (10/100))):
            parent1, parent2 = tournament_selection(population)
            child1, child2 = parent1, parent2
            if rand.uniform(0, 1) >= crossover_prob:
                child1, child2 = crossover(parent1, parent2)
                if check_venue_conflict(child1) >= 1:
                    conflict_repair(child1)
                if check_venue_conflict(child2):
                    conflict_repair(child2)

            # if rand.uniform(0, 1) >= mutation_prob:
            #     mutate(child1)
            #     mutate(child2)

            if evaluate(child1) <= evaluate(parent1):
                child_population.append(child1)
            else:
                child_population.append(parent1)

            if evaluate(child2) <= evaluate(parent2):
                child_population.append(child2)
            else:
                child_population.append(parent2)
        j = int(len(population) * 10 / 100)
        for i in range(j):
            child_population.append(population[i])
        population = child_population
        population.sort(key=evaluate)
        print(evaluate(population[99]))
        # population = population[:len(population) - len(child_population)]+child_population
        generation += 1
    print("Generations:", generation)
    print("Best Chromosome fitness value", evaluate(min(population, key=evaluate)))
    print("Best Chromosome: ", min(population, key=evaluate))
    print(len(population))
        # # if termination criteria are satisfied, stop.
        # if evaluate(min(population, key=evaluate)) == 2 or generation == 500:
        #     print("Generations:", generation)
        #     print("Best Chromosome fitness value", evaluate(min(population, key=evaluate)))
        #     print("Best Chromosome: ", min(population, key=evaluate))
        #     break
        #
        # # Otherwise continue
        # else:
        #     parent1 = tournament_selection(population, 2)
        #     parent2 = tournament_selection(population, 2)
        #     child = crossover(parent1, parent2)
        #     mutate(child)
        #     population[len(population) - 1] = child
        #     population.sort(key=evaluate)
        # generation = generation + 1
        # print("Gen: ", generation)
    # print("Population", len(population))


def cost(solution):
    return 1 / float(evaluate(solution))


# Simple Searching Neighborhood
# It randomly changes timeslot of a class/lab
def ssn(solution):
    rand_slot = rand.randint(1, 300)

    a = rand.randint(0, len(solution) - 1)

    new_solution = copy.deepcopy(solution)
    new_solution[a][1] = rand_slot
    conflict_repair(new_solution)
    return [new_solution]


# Swapping Neighborhoods
# It randomy selects two classes and swap their time slots
def swn(solution):
    a = rand.randint(0, len(solution) - 1)
    b = rand.randint(0, len(solution) - 1)
    new_solution = copy.deepcopy(solution)
    temp = solution[a][1]
    new_solution[a][1] = solution[b][1]

    new_solution[b][1] = temp
    conflict_repair(new_solution)
    # print("Diff", solution)
    # print("Meiw", new_solution)
    return [new_solution]


def acceptance_probability(old_cost, new_cost, temperature):
    if new_cost < old_cost:
        return 1.0
    else:
        return math.exp((old_cost - new_cost) / temperature)


def simulated_annealing():
    alpha = 0.9
    T = 1.0
    T_min = 0.00001

    population = initialize_population(10)  # as simulated annealing is a single-state method
    old_cost = evaluate(population[0])
    print(old_cost)
    # print("Cost of original random solution: ", old_cost)
    # print("Original population:")
    # print(population)

    for __n in range(500):
        new_solution = swn(population[0])
        new_solution = ssn(population[0])
        new_cost = evaluate(new_solution[0])
        ap = acceptance_probability(old_cost, new_cost, T)
        if ap > rand.random():
            population = new_solution
            old_cost = new_cost
        T = T * alpha
    # print(population)
    # print("Cost of altered solution: ", cost(population[0]))
    print("\n------------- Simulated Annealing --------------\n")
    # for lec in population[0]:
    #     print_chromosome(lec)
    print("Score: ", evaluate(population[0]))
    slots = [x[1] for x in population[0]]
    print(len(slots))
    print(len(set(slots)))




genetic_algorithm()
# simulated_annealing()
