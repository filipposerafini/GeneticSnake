import snake
import nn
import plots
import random
import numpy as np
import matplotlib
from matplotlib import pyplot as plt

# GENETICS SETTINGS
POPULATION_SIZE = 100
GOOD_PARENTS = 15
BAD_PARENTS = 5
MUTATION_COUNT = 7
MUTATION_PROBABILITY = 0.2
DROPOUT_COUNT = 3
DROPOUT_PROBABILITY = 0.05

# MISC
SHOW = True
WAIT_STEPS = 300
FPS = None
FITNESS_HISTORY = [[],[],[]]
GRAPH_DPI = 200

class colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[34m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def initial_population():
    population = []
    for _ in range(0, POPULATION_SIZE):
        population.append(nn.NeuralNetwork())
    return population

def calculate_fitness(population):
    game = snake.Game(show=SHOW)
    for _ in population:
        game.snakes.append(snake.Snake(snake.CELL_COUNT/2, snake.CELL_COUNT/2, 5))

    step = 0
    while not game.stop and step < WAIT_STEPS:
        game.render()
        best = game.best_snake()
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
        if all(s.dead for s in game.snakes):
            game.stop = True
        else:
            best = game.best_snake()
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
        if np.random.random() >= 0.5:
            offspring.weights[i] = mother.weights[i]
        else:
            offspring.weights[i] = father.weights[i]
    for i in range(len(offspring.dropout)):
        if np.random.random() >= 0.5:
            offspring.dropout[i] = mother.dropout[i]
        else:
            offspring.dropout[i] = father.dropout[i]
    return offspring

def mutate(offspring):
    mutations = np.random.randint(1, MUTATION_COUNT)
    mutating_index = random.sample(range(offspring.size), mutations)
    for i in mutating_index:
        offspring.weights[i] += np.random.randn()
    return offspring

def dropout(offspring):
    mutations = np.random.randint(1, DROPOUT_COUNT)
    mutating_index = random.sample(range(offspring.layers[0], len(offspring.dropout)), mutations)
    for i in mutating_index:
        offspring.dropout[i] = not offspring.dropout[i]
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
        if np.random.random() < MUTATION_PROBABILITY:
            offspring = mutate(offspring)
        if np.random.random() < DROPOUT_PROBABILITY:
            offspring = dropout(offspring)
        next_population.append(offspring)
    return next_population[:POPULATION_SIZE], parents_fitness

def init_plot(dpi=GRAPH_DPI):
    matplotlib.rcParams['figure.dpi'] = dpi
    plt.figure('Fitness History', facecolor='black')
    plt.style.use('dark_background')
    for i in FITNESS_HISTORY:
        plt.plot(0,0)
    plt.title('Fitness History', color='white')
    plt.xlabel('Generation', color='white')
    plt.ylabel('Fitness', color='white')
    plt.legend(['Average', 'Outline', 'Best'])

def plot_update(parents_fitness):
    plt.figure('Fitness History')
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
    init_plot()
    population = initial_population()
    generation = 0
    while True:
        generation += 1
        print(colors.BOLD)
        print('{:-^100}'.format(' Generation # ' + colors.YELLOW + str(generation) + ' ' + colors.END + colors.BOLD))
        print(colors.END)
        next_population, parents_fitness = genetic_algorithm(population)
        next_population[0].draw()
        plot_update(parents_fitness)
        population = next_population
