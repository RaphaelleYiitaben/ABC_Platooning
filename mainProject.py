import numpy
from neo4j import GraphDatabase
from datetime import datetime
import pylab as plt
from functionProject import construct_path, calculate_fitness, new_sol_Generation


start_time = datetime.now()
cql8 = "Match (n) return count(n) as count"
cql11 = "MATCH (n:RoadPoint)-[r]-(m:RoadPoint) where ID(n) = $node1 and ID(m) = $node2 RETURN r.distance as distance"

uri = "neo4j://localhost:7687"

userName = "neo4j"

password = "test"

graphDB_Driver = GraphDatabase.driver(uri, auth=(userName, password))

# Trucks creation, the truck,departure city, arrival city, travelling time in minutes
trucks = [{"truck": "1", "departure": 92, "arrival": 35},
          {"truck": "2", "departure": 65, "arrival": 17},
          {"truck": "3", "departure": 1, "arrival": 29},
          {"truck": "4", "departure": 98, "arrival": 19},
          {"truck": "5", "departure": 22, "arrival": 5},
          {"truck": "6", "departure": 65, "arrival": 5},
          {"truck": "7", "departure": 67, "arrival": 22},
          {"truck": "8", "departure": 88, "arrival": 65},
          {"truck": "9", "departure": 1, "arrival": 17},
          {"truck": "10", "departure": 98, "arrival": 92}]

with graphDB_Driver.session() as graphDB_Session:
    # variables
    num_FoodSource = 5  # number of food sources. will make up our population
    limit = 10  # 2 is the dimension of the problem
    iteration = 100
    population = []
    trials = []
    Fuelreduction = 0.1
    best_costs = []

    # count number of nodes
    data = graphDB_Session.run(cql8)
    for d in data:
        count_nodes = d.get("count") - 10

    # create matrix that will contain our database
    mat = numpy.zeros((count_nodes, count_nodes))
    i = 0
    while i < count_nodes:
        j = 0
        n = 0
        while j < count_nodes:
            data = graphDB_Session.run(cql11, node1=i, node2=j)  # check if two nodes are connected
            for d in data:
                if bool(d.get("distance")):
                    mat[i][j] = d.get("distance")
            if mat[i][j]:
                n = n+1
                if n == 4:
                    break
            j = j + 1

        i = i + 1

    # population generation
    population = [[numpy.random.uniform(0, 10, count_nodes) for i in range(len(trucks))] for j in range(num_FoodSource)]
    trials = [0 for i in range(len(population))]
    list_fitness = []  # will contrain the list of fitness of the entire population
    list_path = []  # contain the real path of trucs (index of nodes)
    i = 0
    while i < len(population):
        path, population[i] = construct_path(mat, trucks, population[i])
        fitness = calculate_fitness(mat, path, trucks, Fuelreduction)
        list_fitness.append(fitness)
        list_path.append(path)
        i = i + 1

    ##########################            ABC            ##############################
    bestFit = 0  # will contain the best fit
    i = 0
    cost = 100000
    while i in range(iteration):
        ######################### employee phase

        eB = len(population)  # empolyee bee
        x = 0
        while x in range(eB):
            newSolution = new_sol_Generation(x, num_FoodSource, trucks, population)
            path, newSolution = construct_path(mat, trucks, newSolution)
            fitness = calculate_fitness(mat, path, trucks, Fuelreduction)

            if fitness > list_fitness[x]:
                population[x] = newSolution.copy()
                list_fitness[x] = fitness  # change the fitness to put the new fitness
                list_path[x] = path.copy()
            else:
                trials[x] = trials[x] + 1

            x = x + 1

        ######################### Onlooker phase

        oB = len(population)
        list_prob = []  # list of probabilities
        r = 0  # a random number between 0 and 1
        maxFit = max(list_fitness)
        x = 0

        while x in range(len(population)):  # calculate thier probabilities
            list_prob.append(0.9 * (list_fitness[x] / maxFit) + 0.1)
            x = x + 1
        f = 0
        # ensure that an onlooker bee have actually exploit a food source
        x = 0
        while x in range(oB):
            if f == len(population):
                f = 0
            while f < len(population):
                r = numpy.random.uniform(0, 1)
                if r < list_prob[f]:
                    newSolution = new_sol_Generation(x, num_FoodSource, trucks, population)
                    path, newSolution = construct_path(mat, trucks, newSolution)
                    fitness = calculate_fitness(mat, path, trucks, Fuelreduction)
                    if fitness > list_fitness[x]:
                        population[x] = newSolution.copy()
                        list_fitness[x] = fitness  # change the fitness to put the new fitness
                        list_path[x] = path.copy()
                    else:
                        trials[x] = trials[x] + 1
                    f = f + 1
                    break
                if f == len(population):
                    f = 0
                f = f + 1
                # help to start back
            x = x + 1

        ###################### best solution

        if max(list_fitness) > bestFit:
            bestFit = max(list_fitness)
            bestFit_index = list_fitness.index(bestFit)
            print('\n path')
            print(list_path[bestFit_index])
            print('cost')
            cost = (1 / bestFit) - 1
            print(cost)
            best_costs.append(cost)

        ########################## scooter phase

        Max_Trial = max(trials)  # get the max tial of all
        if Max_Trial > limit:
            indices = [index for index, element in enumerate(trials) if element == Max_Trial]  # count the number of times it is in the array
            if len(indices) > 1:
                select = numpy.random.randint(1, len(indices))  # choose one at random
                index_to_be_modified = indices[select - 1]
            else:
                index_to_be_modified = indices[0]

            population[index_to_be_modified] = [numpy.random.uniform(0, 10, count_nodes) for i in range(len(trucks))]

            trials[index_to_be_modified] = 0

            list_path[index_to_be_modified], population[index_to_be_modified] = construct_path(mat, trucks, population[index_to_be_modified])
            list_fitness[index_to_be_modified] = calculate_fitness(mat, list_path[index_to_be_modified], trucks, Fuelreduction)


        i = i + 1

        #####################################

plt.plot(range(0, len(best_costs)), best_costs)
plt.show()
print(datetime.now() - start_time)
