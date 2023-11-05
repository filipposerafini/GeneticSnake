import snake
import nn
import sys
import random
import time
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt

# GENETICS SETTINGS
POPULATION_SIZE = 200
PARENTS = 10
MAX_MUTATIONS = 5
MUTATION_PROBABILITY = 0.1

# MISC
SHOW = True
WAIT_STEPS = 500
FPS = None
DPI = 100

now = datetime.now()

class colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[34m'
    MAGENTA = '\033[95m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def initial_population(start=None):
    population = []
    for _ in range(0, POPULATION_SIZE):
        if start is None:
            population.append(nn.NeuralNetwork(generation=1))
        else:
            population.append(start)
    return population

def calculate_fitness(population, game):

    game.reset()
    for _ in population:
        game.snakes.append(snake.Snake())

    step = 0
    max_score = 0
    prev_best = game.best_snake()

    while not game.stop and step < WAIT_STEPS:
        if game.is_stopped():
            game.end()
            return []
        game.render(step=step)

        for i in range(POPULATION_SIZE):
            inputs = game.snakes[i].get_inputs()

            action = np.argmax(population[i].compute_outputs(inputs))
            if action == 0:
                game.snakes[i].turn_right()
            elif action == 1:
                game.snakes[i].turn_left()
        game.update(FPS)

        if all(s.dead for s in game.snakes):
            game.stop = True
        else:
            best = game.best_snake()
            if best.score > max_score or best is not prev_best:
                max_score = best.score
                step = 0
            step += 1
            prev_best = best

    fitness = []
    for s in game.snakes:
        fitness.append(s.score)

    return fitness

def select_parents(population, fitness):
    sorted_index = list(np.argsort(fitness)[::-1])
    parents = []
    parents_fitness = []
    for i in sorted_index[:PARENTS]:
        parents.append(population[i])
        parents_fitness.append(fitness[i])
    return parents, parents_fitness

def crossover(mother, father, generation):
    offspring = nn.NeuralNetwork(generation=generation)
    for i in range(offspring.size):
        if np.random.random() >= 0.5:
            offspring.weights[i] = mother.weights[i]
        else:
            offspring.weights[i] = father.weights[i]
    return offspring

def mutate(offspring):
    for i in range(offspring.size):
        if np.random.random() < MUTATION_PROBABILITY:
            offspring.weights[i] += np.random.randn()
    return offspring

def genetic_algorithm(population, game, generation):
    # Calculate Fitness
    fitness = calculate_fitness(population, game)
    if not fitness:
        return [], []
    # Select Parents
    parents_pool, parents_fitness = select_parents(population, fitness)
    next_population = parents_pool
    # Generate Offspring
    while len(next_population) < POPULATION_SIZE:
        parents = random.sample(parents_pool, 2)
        mother = parents[0]
        father = parents[1]
        # Crossover
        offspring = crossover(mother, father, generation)
        # Mutate
        offspring = mutate(offspring)
        next_population.append(offspring)
    return next_population[:POPULATION_SIZE], parents_fitness

def init_plot():
    history = [[0], [0]]
    plt.figure('Fitness History')
    plt.plot([0], history[0])
    plt.plot([0], history[1])
    plt.title('Fitness History')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.legend(['Average', 'Best'])
    plt.grid(alpha = 0.5)
    return history

def update_plot(history, generation):
    plt.figure('Fitness History')

    x = list(range(generation + 1));

    for i, line in enumerate(plt.gca().lines):
        line.set_xdata(x)
        line.set_ydata(history[i][:])
    plt.gca().relim()
    plt.gca().autoscale_view()
    plt.pause(0.05)

if __name__ == '__main__':

    args = len(sys.argv)

    if args == 1:
        population = initial_population()
    elif args == 2:
        filename = sys.argv[1]
        if filename.endswith('.json'):
            population = initial_population(nn.fromJSON(filename))
        else:
            print('usage: genetic.py [snake_nn.json]')
            sys.exit()
    else:
        print('usage: genetic.py [snake_nn.json]')
        sys.exit()

    game = snake.Game(show=SHOW)
    generation = 0
    overall_best = 0
    history = init_plot()

    while True:
        generation += 1
        next_population, fitness = genetic_algorithm(population, game, generation)
        if not next_population and not fitness:
            break
        
        print(colors.BOLD + 'Generation # ' + colors.YELLOW + str(generation) + colors.END + '\n')

        avg_fit = np.average(fitness)
        history[0].append(avg_fit)
        print(colors.BOLD + colors.GREEN + 'Average: ' + str(avg_fit) + colors.END)

        best_fit = fitness[0]
        history[1].append(best_fit)
        print(colors.BOLD + colors.MAGENTA + 'Best: ' + str(best_fit) + colors.END + '\n')

        update_plot(history, generation)

        if best_fit > overall_best:
            overall_best = best_fit
            nn.toJSON('save/snake_nn_' + now.strftime('%Y%m%d-%H:%M') + '.json', next_population[0])
            print('-----------------')
            print(colors.BOLD + colors.YELLOW + 'NEW HIGH SCORE!!!' + colors.END)
            print('-----------------\n')

        population = next_population
