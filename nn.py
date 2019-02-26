import numpy as np

INPUTS = 5
HIDDEN1 = 7
HIDDEN2 = 5
OUTPUTS = 3

class NeuralNetwork:

    def __init__(self, dropout_prob=0, inputs=INPUTS, outputs=OUTPUTS, h_layers=[HIDDEN1, HIDDEN2]):
        self.layers = [0, inputs] + h_layers + [outputs]
        self.size = 0
        self.h_layers = len(h_layers)
        self.dropout = []
        for i in range(1, len(self.layers) - 1):
            self.size += self.layers[i] * self.layers[i + 1]
            dropout = np.random.random(self.layers[i + 1])
            self.dropout.append(dropout > dropout_prob)
        self.weights = np.random.rand(self.size) * 2 - 1

    def get_weights(self, layer):
        start = 0
        for i in range(layer + 1):
            start += self.layers[i] * self.layers[i+1]
        end = start + self.layers[layer+1] * self.layers[layer+2]
        return(self.weights[start:end].reshape(self.layers[layer+1], self.layers[layer+2]))

    def softmax(self, z):
        e_z = np.exp(z - np.max(z))
        return e_z / e_z.sum(axis=0)

    def relu(self, z):
        return z * (z > 0)

    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def forward_propagation(self, inputs, weights, dropout, is_output=False):
        z = np.matmul(inputs, weights)
        if is_output:
            a = self.softmax(z)
        else:
            a = self.relu(z)
        a = np.multiply(a, dropout)
        return a

    def compute_outputs(self, inputs):
        x = inputs
        for i in range(self.h_layers):
            a = self.forward_propagation(x, self.get_weights(i), self.dropout[i])
            x = a

        return self.forward_propagation(x, self.get_weights(self.h_layers), self.dropout[self.h_layers], is_output=True)
