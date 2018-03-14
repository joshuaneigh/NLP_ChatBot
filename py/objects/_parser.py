#!/usr/bin/python
# Author: 
# Version: 21 February 2018
# Email: 

from rake_nltk import Rake
import nltk


class Parser:
    def __init__(self):
        pass

    def parse(self, m):
        r = Rake()
        r.extract_keywords_from_text(m)
        words = r.get_ranked_phrases()
        word = ""
        for i in words:
            word += i + " "
        return word

    def extractnoun(self, text):
        Nouns = " "
        for word, pos in nltk.pos_tag(nltk.word_tokenize(str(text))):
            if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS'):
                Nouns += word + " "
        return Nouns






if __name__ == "__main__":
    print("Testing....")
    p = Parser()
    testString = "Hello, How are you?"
    output = p.parse(testString)
    print(output)
    print('Extracted Nouns is ' + p.extractnoun(testString))


