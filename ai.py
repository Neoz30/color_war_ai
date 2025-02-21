from random import randint, random


class Node:
    def __init__(self):
        self.links = []
        self.value = 0
        self.weight = 0
        self.bias = 0

    def compute(self):
        c = self.value * self.weight + self.bias
        for link in self.links:
            link.value += c

    def mutate(self):
        self.weight = randint(-10, 10)
        self.bias = randint(-10, 10)


class Network:
    def __init__(self, inputs: int, outputs: int, hidden_layer: int, hidden_node: int):
        self.inputs = [Node() for _ in range(inputs)]
        self.outputs = [Node() for _ in range(outputs)]
        self.hidden = [
            [
                Node() for _ in range(hidden_node)
            ] for _ in range(hidden_layer)
        ]

    def compute(self):
        layers = list(self.inputs) + self.hidden + list(self.outputs)
        for layer in layers:
            for node in layer:
                node.compute()

    def mutate(self, luck: float):
        layers = list(self.inputs) + self.hidden + list(self.outputs)
        for layer in layers:
            for node in layer:
                if random() > luck:
                    node.mutate()

    def shuffle(self):
        self.mutate(1)
