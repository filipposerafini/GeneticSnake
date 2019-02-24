import numpy as np

INPUTS = 5
HIDDEN1 = 6
HIDDEN2 = 4
OUTPUTS = 3

class NeuralNetwork:

    def __init__(self):
        self.weights = np.random.rand(INPUTS*HIDDEN1 + HIDDEN1*HIDDEN2 + HIDDEN2*OUTPUTS) * 2 - 1

    def get_weights(self, start, input_layer, output_layer):
        return self.weights[start:start + input_layer*output_layer].reshape(input_layer, output_layer)

    def softmax(self, z):
        return np.exp(z.T) / np.sum(np.exp(z.T), axis=1).reshape(-1, 1)

    def relu(self, z):
        return z * (z > 0)

    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def compute_outputs(self, inputs):
        Z1 = np.matmul(inputs, self.get_weights(0, INPUTS, HIDDEN1))
        A1 = self.relu(Z1)
        Z2 = np.matmul(A1, self.get_weights(INPUTS*HIDDEN1, HIDDEN1, HIDDEN2))
        A2 = self.relu(Z2)
        Z3 = np.matmul(A2, self.get_weights(INPUTS*HIDDEN1 + HIDDEN1*HIDDEN2, HIDDEN2, OUTPUTS))
        A3 = self.relu(Z3)
        return A3
