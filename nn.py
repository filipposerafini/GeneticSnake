import numpy as np
import matplotlib
import json
from matplotlib import pyplot as plt

INPUTS = 9
HIDDEN = [12]
OUTPUTS = 3

LAYERS_DISTANCE = 250
NEURONS_DISTANCE = 100
RADIUS = 20

INPUT_COLOR = (0, 1, 0)
OUTPUT_COLOR = (1, 0, 1)
NEURON_COLOR = (0, 0, 0)
POSITIVE_WEIGHT = (1, 0, 0)
NEGATIVE_WEIGHT = (0, 0, 1)

DPI = 100

class NeuralNetwork:

    def __init__(self, generation=0, inputs=INPUTS, outputs=OUTPUTS, hidden=HIDDEN, weights=None):
        self.generation = generation
        self.layers = [inputs] + hidden + [outputs]
        self.h_layers = len(hidden)
        self.size = 0
        for i in range(1, len(self.layers)):
            self.size += self.layers[i - 1] * self.layers[i]
        if weights is None:
            self.weights = np.random.randn(self.size).tolist()
        else:
            self.weights = weights

    def get_weights(self, layer):
        start = 0
        for i in range(layer):
            start += self.layers[i] * self.layers[i+1]
        end = start + self.layers[layer] * self.layers[layer+1]
        weights = np.array(self.weights)
        weights = weights[start:end].reshape(self.layers[layer], self.layers[layer+1])
        return weights

    def softmax(self, z):
        e_z = np.exp(z - np.max(z))
        return e_z / e_z.sum(axis=0)

    def relu(self, z):
        return z * (z > 0)

    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def forward_propagation(self, inputs, weights, is_output=False):
        z = np.matmul(inputs, weights)
        if is_output:
            a = self.softmax(z)
        else:
            a = self.relu(z)
        return a

    def compute_outputs(self, inputs):
        x = inputs
        for i in range(self.h_layers):
            a = self.forward_propagation(x, self.get_weights(i))
            x = a
        return self.forward_propagation(x, self.get_weights(self.h_layers), is_output=True)

    def draw(self):
        matplotlib.rcParams['figure.dpi'] = DPI
        plt.figure('Neural Network')
        plt.clf()
        for layer in range(1, len(self.layers)):
            weights = self.get_weights(layer - 1).T
            for neuron in range(self.layers[layer]):
                for w, weight in enumerate(weights[neuron]):
                    self.__draw_weight(layer, neuron, self.layers[layer], w,
                            self.layers[layer-1], weight)
        for layer in range(len(self.layers)):
            for neuron in range(self.layers[layer]):
                if layer == 0:
                    color = INPUT_COLOR
                elif layer == len(self.layers) - 1:
                    color = OUTPUT_COLOR
                else:
                    color = NEURON_COLOR
                self.__draw_neuron(layer, neuron, self.layers[layer], color)
        plt.axis('scaled')
        plt.axis('off')
        plt.pause(0.1)

    def __get_neuron_coord(self, layer, index, total):
        x = layer * LAYERS_DISTANCE
        y = ((total/2) - 0.5) * NEURONS_DISTANCE - index * NEURONS_DISTANCE
        return x, y

    def __draw_neuron(self, layer, index, total, color):
        x, y = self.__get_neuron_coord(layer, index, total)
        circle = plt.Circle((x, y), radius=RADIUS, color=color)
        plt.gca().add_patch(circle)

    def __draw_weight(self, layer, src, total_src, dst, total_dst, weight):
        x_src, y_src = self.__get_neuron_coord(layer, src, total_src)
        x_src = x_src - RADIUS
        x_dst, y_dst = self.__get_neuron_coord(layer - 1, dst, total_dst)
        x_dst = x_dst + RADIUS
        if weight > 0:
            color = POSITIVE_WEIGHT
        else:
            color = NEGATIVE_WEIGHT
        line = plt.Line2D((x_src, x_dst), (y_src, y_dst), color=color)
        line.set_linewidth(abs(weight))
        plt.gca().add_line(line)

def toJSON(filename, neural_net):
    with open(filename, "w") as f:
        f.write(json.dumps(neural_net, default=lambda o: o.__dict__, 
        sort_keys=True, indent=4))

def fromJSON(filename):
    with open(filename, "r") as f:
        loaded = json.load(f)
        inputs = loaded['layers'][0]
        outputs = loaded['layers'][-1]
        hidden = loaded['layers'][1:-1]
        return NeuralNetwork(generation=loaded['generation'],inputs=inputs, outputs=outputs, hidden=hidden, weights=loaded['weights'])
