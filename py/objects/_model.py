#!/usr/bin/python
# Author: Zachary Chandler
# Version: 21 February 2018
# Email: zachary.a.chandler96@gmail.com

import pickle
import random
from _parser import Parser

class Model:
    def __init__(self):
        self.parser = Parser()
        self.responses = {}
        self.huh = []

        trainSet1(self)
        trainSet2(self)

    def train(self, m1, m2):
        key = self.parser.parse(m1)

        if key in self.responses:
            responses = self.responses[key]
            found = False
            for pair in responses:
                if pair[0] == m2:
                    pair[1] += 1
                    found = True
                    break

            if not found:
                responses.append([m2, 1])
        else:
            self.responses[key] = [[m2, 1]]

    def __getResponse(self, responses):
        total = 0

        for r in responses:
            total += r[1]

        choice = random.randint(0, total)
        total = 0
        
        for r in responses:
            total += r[1]
            if choice <= total:
                return r[0]

        # shouldn't ever occur
        return "error: the random element of my response choice has failed"

    def __getUnkownResponse(self):
        return "pass"
    
    def findResponse(self, m):
        key = self.parser.parse(m)

        if not key in self.responses:
            key = None

        return self.__getResponse(self.responses[key])


def trainSet1(model):
    model.train("test1", "test2")
    model.train("test1", "test3")
    model.train("test1", "test4")
    
    model.train("test2", "test5")

def trainSet2(model):
    model.train(None, "what do you mean?")

def pickleModel(model):
    pickle.dump(model, open("model.p", "wb"))
    
if __name__ == "__main__":
    model = Model()
    pickleModel(model)
##    print(model.findResponse(""))
    print("...")
