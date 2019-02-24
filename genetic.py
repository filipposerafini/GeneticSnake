import random
import numpy as np
import nn
import snake
from operator import attrgetter
import matplotlib
import matplotlib.pyplot as plt

# GENETICS SETTINGS
POPULATION_SIZE = 100
GOOD_PARENTS = 12
BAD_PARENTS = 3
MUTATION_COUNT = 6
MUTATION_PROBABILITY = 0.2

# MISC
HIDDEN = False
WAIT_STEPS = 300
FPS = None
FITNESS_HISTORY = [[],[],[]]
GRAPH_DPI = 200

# COLORS
class colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    BLUE = '\033[34m'
    END = '\033[0m'

def initial_population():
    population = []
    for _ in range(0, POPULATION_SIZE):
        population.append(nn.NeuralNetwork())
    return population

def calculate_fitness(population):
    game = snake.Game(hidden=HIDDEN)
    for _ in population:
        game.snakes.append(snake.Snake(snake.CELL_COUNT/2, snake.CELL_COUNT/2, 5))

    step = 0
    while step < WAIT_STEPS:
        game.render()
        best = max(game.snakes, key=attrgetter('score'))
        old_apple = best.apple
        for i in range(POPULATION_SIZE):
            apple = game.snakes[i].observe_apple().to_norm_relative()
            obstacles = [obstacle.to_norm_relative() for obstacle in game.snakes[i].observe_obstacle()]
            inputs = [apple[0], apple[1], obstacles[0][0], obstacles[1][0], obstacles[2][0]]
            action = np.argmax(population[i].compute_outputs(inputs))
            if action == 1:
                game.snakes[i].turn_right()
            elif action == 2:
                game.snakes[i].turn_left()
        game.update(FPS)
        game.stop = True
        for s in game.snakes:
            if not s.dead:
                game.stop = False
                break
        if game.stop:
            break
        best = max(game.snakes, key=attrgetter('score'))
        if old_apple is not best.apple:
            step = 0
        step += 1
    fitness = []
    for s in game.snakes:
        fitness.append(s.score)
    game.end()
    return fitness

def select_parents(population, fitness):
    sorted_index = list(np.argsort(fitness)[::-1])
    parents = []
    parents_fitness = []
    for i in sorted_index[:GOOD_PARENTS]:
        parents.append(population[i])
        parents_fitness.append(fitness[i])
    lucky_index = random.sample(sorted_index[GOOD_PARENTS:], BAD_PARENTS)
    for lucky in lucky_index:
        parents.append(population[lucky])
        parents_fitness.append(fitness[lucky])
    return parents, parents_fitness

def crossover(mother, father):
    offspring = nn.NeuralNetwork()
    for i in range(offspring.size):
        if random.random() >= 0.5:
            offspring.weights[i] = mother.weights[i]
        else:
            offspring.weights[i] = father.weights[i]
    return offspring

def mutate(offspring):
    mutations = random.randint(1, MUTATION_COUNT)
    mutating_index = random.sample(range(offspring.size), mutations)
    for i in mutating_index:
        offspring.weights[i] = (random.random()*2 - 1)
    return offspring

def genetic_algorithm(population):
    fitness = calculate_fitness(population)
    parents_pool, parents_fitness = select_parents(population, fitness)
    avg_fit = np.average(parents_fitness)
    print(colors.BOLD, end='')
    print('{: ^100}'.format(colors.GREEN + 'Average: ' + colors.END + colors.BOLD + str(avg_fit)))
    print(colors.END)
    best_fit = np.max(parents_fitness)
    print(colors.BOLD, end='')
    print('{: ^100}'.format(colors.BLUE + 'Best: ' + colors.END + colors.BOLD + str(best_fit)))
    print(colors.END, end='')
    next_population = parents_pool
    while len(next_population) < POPULATION_SIZE:
        parents = random.sample(parents_pool, 2)
        mother = parents[0]
        father = parents[1]
        offspring = crossover(mother, father)
        if random.random() < MUTATION_PROBABILITY:
            next_population.append(mutate(offspring))
        else:
            next_population.append(offspring)
    return next_population[:POPULATION_SIZE], parents_fitness

def plot_update(parents_fitness):
    FITNESS_HISTORY[0].append(np.average(parents_fitness))
    FITNESS_HISTORY[1].append(np.max(FITNESS_HISTORY[0][:]))
    FITNESS_HISTORY[2].append(np.max(parents_fitness))
    x = np.arange(1,len(FITNESS_HISTORY[0])+1)
    for i, line in enumerate(plt.gca().lines):
        line.set_xdata(x)
        line.set_ydata(FITNESS_HISTORY[i][:])
    plt.gca().relim()
    plt.gca().autoscale_view()
    plt.pause(0.05)

if __name__ == '__main__':
    population = initial_population()
    generation = 0
    matplotlib.rcParams['figure.dpi'] = GRAPH_DPI
    for i in FITNESS_HISTORY:
        plt.plot(0,0)
    plt.title("Fitness History")
    plt.xlabel("Generation")
    plt.ylabel("Average Fitenss")
    plt.legend(["Average", "Outline", "Best"])
    while True:
        generation += 1
        print(colors.BOLD)
        print('{:-^100}'.format(' Generation # ' + colors.YELLOW + str(generation) + ' ' + colors.END + colors.BOLD))
        print(colors.END)
        next_population, parents_fitness = genetic_algorithm(population)
        plot_update(parents_fitness)
        population = next_population
