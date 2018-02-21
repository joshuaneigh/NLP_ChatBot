#!/usr/bin/python
# Author: Zachary Chandler
# Version: 21 February 2018
# Email: zachary.a.chandler96@gmail.com

import pickle
from _parser import Parser

class Model:
    def __init__(self):
        self.parser = Parser()
        self.responses = {}
        self.huh = []

        trainSet1(self)
        trainSet2(self)

    def train(self, m1, m2):
        pass

    def findResponse(self, k):
        return "pass"

def trainSet1(model):
    model.train("test1", "test2")

def trainSet2(model):
    pass

def pickleModel(model):
    pickle.dump(model, open("model.p", "wb"))
    
if __name__ == "__main__":
    model = Model()
##    pickleModel(model)
    print("...")
