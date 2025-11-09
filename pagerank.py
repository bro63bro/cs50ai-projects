import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    
    tr_model = dict()
    
    # Assign probabilities to linked pages
    for i in corpus[page]:
        tr_model[i] = damping_factor*(1/len(corpus[page])) + (1-damping_factor)*(1/len(corpus))
    # Assign probabilities to non-linked pages
    for j in corpus.keys():
        if j not in tr_model.keys():
            tr_model[j] = (1-damping_factor)*(1/len(corpus))
    
    return tr_model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    t = 0
    sample_dict = dict()
    sample = random.choice(list(corpus.keys()))
    
    # Choose the next page according to the transition model
    # and update that page's count along the way
    while t <= n:
        tr = transition_model(corpus, sample, damping_factor)
        next_sample = random.choices(
            list(tr.keys()), 
            weights = list(tr.values()), 
            k = 1)    # This function returns a list, not the element itself
        if next_sample[0] in sample_dict.keys(): 
            sample_dict[next_sample[0]] += 1
        else:
            sample_dict[next_sample[0]] = 1
        sample = next_sample[0]
        t += 1
        
    
    # Scale by n to get sample probability distribution
    for i in sample_dict.keys():
        sample_dict[i] = sample_dict[i]/n
    
    return sample_dict


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    it_dict = dict()
    
    # Keep track of the differences of values between iterations
    diff_dict = dict()
    
    # Initialize PageRank values in our dictionary
    for p in corpus.keys():
        it_dict[p] = 1/len(corpus)
    
    # Caculate the total probability of being on page p
    # First makes list of all pages linking to p
    def pagerank(p):
        list_p = list()
        for i in corpus.keys():
            if p in corpus[i]:
                list_p.append(i)
        # Contribution of all the pages linking to p
        k = 0
        for i in list_p:
            k += it_dict[i]/len(corpus[i])
        new_pr = (1-damping_factor)/len(corpus) + damping_factor*k
    
        # Update differences dictionary by abosolute value 
        diff_dict[p] = abs(new_pr - it_dict[p])
        
        # Update main dictionary
        it_dict[p] = new_pr
        
    # Updates PageRank for each page in the corpus    
    def update_pages(corpus):
        for p in corpus.keys():
            pagerank(p)
    
    # Check whether any differences exceed threshold
    switch = True
    while switch == True:
        switch = False
        update_pages(corpus)
        for i in diff_dict.values():
            if i > 0.001:
                switch = True
                
    return it_dict


if __name__ == "__main__":
    main()
