import spacy
import math
import numpy as np

#nlp = spacy.load('en_core_web_md') 

def solve(s1, s2):
    import scipy
    vector_1 = np.mean([model[word] for word in s1],axis=0)
    vector_2 = np.mean([model[word] for word in s2],axis=0)
    cosine = scipy.spatial.distance.cosine(vector_1, vector_2)
    print('Word Embedding method with a cosine distance asses that our two sentences are similar to',round((1-cosine)*100,2),'%')
'''
while 1:
	li = input().split()
	tokens = nlp(" ".join(li))
	print (tokens[0].similarity(tokens[1]))
'''

solve(['hello','there'], ['hi', 'there'])

'''
[[0.6337646, 'in'], [0.6337646, 'check'], [0.6086773, 'my'],
[0.5996465, 'mean'], [0.5176737, 'megan'], [0.5107421, 'no'],
[0.47416186, 'is'], [0.4573794, 'no'], [0.4573794, 'i'],
[0.4573794, 'havent'], [0.4573794, 'have'], [0.4573794, 'dragon'],
[0.4573794, 'attention'], [0.4573794, 'a'], [0.45120275, 'its'],
[0.4434555, 'uhoherror'], [0.44196677, 'this'], [0.44196677, 'hours'],
[0.43791872, 'they'], [0.41430074, 'have']]
'''