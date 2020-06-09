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
        # a 3 x 118 matrix where three rows are professor list, timeslot, and room id, room id can be ignored since all the
        # rooms are defined by their number.
        chromosome = []
        booked_slots = []
        # una_slots = list(unavailable_timeslot)
        for present in staff_to_presentation:
            slot = rand.randint(0, 299)
            free = True
            staff_slots = []
            for staff in present.staff:
                staff_slots = staff_slots + unavailable_staff[staff - 1]
            while slot in staff_slots or slot in booked_slots or slot in unavailable_timeslot:
                slot = rand.randint(0, 299)

            booked_slots.append(slot)
            # una_slots.append(slot)
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
    return score


def evaluate(chromosomes):
    score = 0
    score = score + check_venue_availability(chromosomes)
    score = score + check_staff_availability(chromosomes)
    return score


def tournament_selection(population, k):
    best = None
    for i in range(k):
        ind = population[rand.randint(0, len(population) - 1)]
        if best is None or evaluate(ind) > evaluate(best):
            best = ind
    return best


# Modified Combination of Row_reselect, Column_reselect
def mutate(chromosome):
    # print("Before mutation: ", end="")
    # printChromosome(chromosome)
    ran_slot = rand.randint(0, 300)
    a = rand.randint(0, len(chromosome) - 1)

    chromosome[a][1] = ran_slot

    # print("After mutation: ", end="")
    # printChromosome(chromosome)


def crossover(p1, p2):
    # a = random.randint(0, len(population) - 1)
    # b = random.randint(0, len(population) - 1)
    child = [p1[x1] for x1 in range(len(p1) - 59)] + [p2[x2] for x2 in range(59, len(p2))]
    return child


def genetic_algorithm():
    generation = 0
    population = initialize_population(10)
    print("Original population:")
    print(population)
    print("Original costs:")
    for pop in population:
        print(evaluate(pop))
    print("\n------------- Genetic Algorithm --------------\n")
    population.sort(key=evaluate)
    for pop in population:
        print(evaluate(pop))


    while True:
        # if termination criteria are satisfied, stop.
        if evaluate(max(population, key=evaluate)) == 0 or generation == 500:
            print("Generations:", generation)
            print("Best Chromosome fitness value", evaluate(max(population, key=evaluate)))
            print("Best Chromosome: ", max(population, key=evaluate))
            break

        # Otherwise continue
        else:
            parent1 = tournament_selection(population, 5)
            parent2 = tournament_selection(population, 5)
            child = crossover(parent1, parent2)
            mutate(child)
            population[len(population) - 1] = child
            population.sort(key=evaluate)
        generation = generation + 1
        # print("Gen: ", generation)
    # print("Population", len(population))

genetic_algorithm()