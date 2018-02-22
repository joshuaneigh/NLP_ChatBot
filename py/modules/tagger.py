#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Joshua Neighbarger
# Version: 22 February 2018
# Email: jneigh@uw.edu

""" MyTagger

Custom NLTK tagger, based on default, unigram, bigram, and trigram taggers. The used taggers utilize a backoff so that
the trained tagger remains small.

Attributes:
    CUTOFF (int): Determines the number of occurrences required for the next tagger to replace the tag. The lower this
        value, the higher the accuracy will likely be, but the larger the trained file size is likely to be.

Todo:
    * Replace words not in lexicon to UNK.
    * Save and load tagger to pickle.
"""
"""Train the tagger.

        Training data is separated from the last 10 percent of the given corpus, which will be used to evaluate the
        tagger.

        Args:
            corpus: The corpus on which to train the tagger.

        Returns:
            The estimated accuracy of the tagger
        """

import nltk
from nltk.corpus import *
from pickle import dump, load

CUTOFF = 2


class MyTagger:

    def __init__(self, path: str=None):
        self.isTrained = False
        self.path = path
        if path:
            try:
                with open(path, 'rb') as src:
                    self.tagger = load(src)
            except Exception:  # Broad Exception intentional; code not complete
                print("Pickle dump could not be loaded at path: ", path)
                pass

    def train(self, corpus) -> float:
        sents = corpus.tagged_sents(corpus.fileids())
        training_data = sents[int(len(sents) * 0.9):]
        testing_data = sents[:int(len(sents) * 0.1)]
        t0 = nltk.DefaultTagger('NN')
        t1 = nltk.UnigramTagger(training_data, cutoff=CUTOFF, backoff=t0)
        t2 = nltk.BigramTagger(training_data, cutoff=CUTOFF, backoff=t1)
        t3 = nltk.TrigramTagger(training_data, cutoff=CUTOFF, backoff=t2)
        self.tagger = t3
        if self.path:
            self.save(self.path)
        return self.evaluate(testing_data)

    def evaluate(self, corpus: list) -> float:
        return self.tagger.evaluate(corpus)

    def tag(self, text) -> list:
        if not self.tagger:
            raise Exception("")
        else:
            if isinstance(text, str):
                return self.tagger.tag(text.split())
            elif isinstance(text, list) and isinstance(text[0], str):
                return self.tagger.tag(text)

    def save(self, path):
        with open(path, 'wb') as out:
            dump(self.tagger, out, -1)


def test_tag():
    message = input("What to tag?  ")
    tagger = MyTagger()
    try:
        print("Accuracy:", tagger.train(brown))
    except ZeroDivisionError:
        pass
    print(tagger.tag(message))


def get_commands():
    return {"tag": (test_tag, 0, "Tags the passed message and outputs to the console.")}


def launch():
    test_tag()
