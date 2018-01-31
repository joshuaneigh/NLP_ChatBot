#!/usr/bin/python
# Author: Joshua Neighbarger
# Version: 30 January 2018
# Email: jneigh@uw.edu

import nltk

def launch():
    s = input("Sentence to parse?  ")
    tokens = nltk.word_tokenize(s)
    tagged = nltk.pos_tag(tokens)
    print(tagged)
