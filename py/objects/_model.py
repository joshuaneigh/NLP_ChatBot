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

    def findResponse(self, m):
        if (m != None):
            key = self.parser.parse(m)

            if not key in self.responses:
                key = None
        else:
            key = None
        
        return self.__chooseResponse(self.responses[key])
    
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

    def __chooseResponse(self, possibleResponses):
        total = 0

        for r in possibleResponses:
            total += r[1]

        choice = random.randint(0, total)
        total = 0
        
        for r in possibleResponses:
            total += r[1]
            if choice <= total:
                return r[0]

        # shouldn't ever occur
        return "error: the random element of my response choice has failed"

    def __getUnkownResponse(self):
        return "pass"
    

def trainCustom(model):
    trainFromFile("..\\..\\training\\custom\\generic.txt", model)

def trainCornwell(model):
     trainFromFile("..\\..\\training\\cornwell\\simplified.txt", model)

def trainNPS(model):
    trainFromFile("..\\..\\training\\nps-subset\\10-26-teens_706posts.xml.txt", model)
    trainFromFile("..\\..\\training\\nps-subset\\11-08-teens_706posts.xml.txt", model)
    trainFromFile("..\\..\\training\\nps-subset\\11-09-teens_706posts.xml.txt", model)

def trainUnkown(model):
    model.train(None, "hmm")
    model.train(None, "okay")
    model.train(None, "yeah")

def trainFromFile(fileName, model):
    f = open(fileName, "r")
    last = None

    for line in f:
        if line.isspace():
            line = None
        else:
            line = line[:-1]
        
        if last != None and line != None:
            model.train(last, line)
        
        last = line
        
    f.close()

def pickleModel(model):
    pickle.dump(model, open("model.p", "wb"))

def unpickleModel():
	return pickle.load(open("model.p", "rb"))

if __name__ == "__main__":
    model = Model()
    
    trainCornwell(model)
    trainCustom(model)
    trainNPS(model)
    trainUnkown(model)
    
##    print(model.findResponse(None))
##    print(model.findResponse("hi"))
    
    pickleModel(model)
