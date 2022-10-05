from collections import Counter
import numpy as np


def construct_path(mat, trucks, solution):
    finalPath = []
    i = 0
    while i in range(len(trucks)):

        newpath=[]
        # arrange the indexes from small to big

        indexes = np.argsort(solution[i])
        path = indexes.tolist().copy()
        # make sure that the first node is the departure node
        newpath.append(trucks[i]["departure"])
        f = 0
        # form the necesary path from departure to arrival
        while f in range(len(newpath)):

            path = [x for x in path if x not in newpath]
            f2 = 0
            while f2 in range(len(path)):
                if mat[newpath[f]][path[f2]]:
                    newpath.append(path[f2])
                    break
                else:
                    f2 = f2 + 1
            if trucks[i]["arrival"] == newpath[-1]:
                break
            f = f + 1
        while trucks[i]["arrival"] != newpath[-1]:
            np.random.shuffle(solution[i])
            newpath = []
            # arrange the indexes from small to big

            indexes = np.argsort(solution[i])
            path = indexes.tolist().copy()
            # make sure that the first node is the departure node
            newpath.append(trucks[i]["departure"])
            f = 0
            # form the necesary path from departure to arrival
            while f in range(len(newpath)):

                path = [x for x in path if x not in newpath]
                f2 = 0
                while f2 in range(len(path)):
                    if mat[newpath[f]][path[f2]]:
                        newpath.append(path[f2])
                        break
                    else:
                        f2 = f2 + 1
                if trucks[i]["arrival"] == newpath[-1]:
                    break
                f = f + 1
        finalPath.append(newpath)
        i = i + 1
    return finalPath, solution


def calculate_fitness(mat, path, trucks, Fuelreduction):
    # count the number of times that an edge is traversed
    Templist = []  # list of all traversed edges
    i = 0
    while i in range(len(trucks)):
        C = zip(path[i], path[i][1:])  # create edges that have been traversed by pairing up nodes
        for f in C:
            Templist.append(f)
        i = i + 1
    counts = Counter(Templist)  # will contain the sum X for each truck on an edge
    # calculation of the over all cost using the formula
    cost = 0.0
    totalCost = 0.0
    j = 0
    Templist = list(dict.fromkeys(Templist))
    while j in range(len(Templist)):
        cost = (mat[Templist[j][0]][Templist[j][1]]) * (counts[Templist[j]] - (Fuelreduction * (counts[Templist[j]] - 1)))
        totalCost = totalCost + cost

        j = j + 1

    fitness = 1 / (1 + totalCost)  # since cost is greater than zero

    return fitness

def new_sol_Generation(x, nF, trucks, list_population):
    xp = np.random.choice([i for i in range(0, nF) if i not in [x]])  # a randomly selected partner excluding x
    i = np.random.randint(0, len(trucks) - 1)  # select a random column
    phi = np.random.uniform(0, 0.4)  # probability between 0 and 1

    xnew = list_population[x][i] + phi * (list_population[x][i] + list_population[xp][i])  # the newly created solution

    presolution = list_population[x].copy()
    presolution[i] = xnew.copy()  # insert the solution in the foodsource

    return presolution