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

    def train(self, m1, m2):
        if m1 != None:
            key = self.parser.parse(m1)
        else:
            key = None

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
        if (m != None):
            key = self.parser.parse(m)
        else:
            key = None
        
        if not key in self.responses:
            key = None

        return self.__getResponse(self.responses[key])


def trainSet1(model):
    pass

def trainSet2(model):
    model.train(None, "what do you mean?")

def pickleModel(model):
    pickle.dump(model, open("model.p", "wb"))

def unpickleModel():
	return pickle.load(open("model.p", "rb"))
	
if __name__ == "__main__":
##    model = unpickleModel()
##    trainSet1(model)
##    trainSet2(model)
##    pickleModel(model)
##    print(model.findResponse(None))
##    print("...")
    pass
