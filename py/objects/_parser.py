#!/usr/bin/python
# Author: 
# Version: 21 February 2018
# Email: 

from rake_nltk import Rake

class Parser:
    def __init__(self):
        pass

    def parse(self, m):
        r = Rake()
        r.extract_keywords_from_text(m)
        return r.get_ranked_phrases()
    
if __name__ == "__main__":
    print("Testing....")
    p = Parser()
    testString = "Hello, How's everything"
    output = p.parse(testString)
    print(output)

