import nltk
import sys
from nltk.tokenize import NLTKWordTokenizer
import re

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """

S -> NP VP | NP VP Conj VP | NP VP PP | NP VP AdvP | NP VP Conj VP PP

NP -> Det AdjP N | Det N | N | NP Conj NP | Det AdjP N PP | Det N PP

VP -> V | V NP | V NP PP | V AdvP | V PP | V AdvP PP | V NP AdvP

PP -> P NP

AdvP -> Adv | Adv PP

AdjP -> Adj | Adj Conj Adj | Adj Adj Adj

"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    
    raw_list = NLTKWordTokenizer().tokenize(sentence)
    my_list = []
    
    for word in raw_list:
        
        # Check that only alphabetic characters are present
        if re.match("^[a-zA-Z]+$", word):
            my_list.append(word.lower())
    return my_list
    

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    
    my_list = []
    
    # Gather all subtrees that are NP
    for s in tree.subtrees(lambda x: x.label() == "NP"):
        
        # Check whether any of its subtrees are NP
        for st in s.subtrees():
            
            # If any of them are, skip to the next NP subtree
            if st.label() == "NP":
                break
        my_list.append(s)
    
    return my_list


if __name__ == "__main__":
    main()
