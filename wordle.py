import pickle
import os
from nltk import edit_distance
from random import choice

# Load corpus with caching
corpus_file = 'wordle_corpus.pkl'

if os.path.exists(corpus_file):
    with open(corpus_file, 'rb') as f:
        corpus = pickle.load(f)
else:
    from nltk.corpus import words
    corpus = list(set([w.lower() for w in words.words() if len(w)==5]))
    with open(corpus_file, 'wb') as f:
        pickle.dump(corpus, f)

alphabet = [chr(i) for i in range(ord('a'), ord('z')+1)]
required = []
win = False
live = False
convenience = {2:'1',1:'0',0:'N'}

# set mode
wtype = ''
while wtype == '':
	print('Word options: INPUT | RANDOM | LIVE')
	wtype = input('Word type?: ').upper()
	if wtype == 'INPUT':
		secret = input('Input secret word: ').lower()
		secret = secret[:5]
	elif wtype == 'RANDOM':
		secret = choice(corpus)
	elif wtype == 'LIVE':
		live = True
	else:
		wtype = ''

for i in range(6):
	# read guess, outcome
	if i==0:
		instr = 'Guess? F{EARTH}: '
	else:
		instr = 'Guess?: '
	guess = input(instr).lower()

	if live: # only input outcome codes if playing live game
		if i==0:
			instr = 'Outcome? F{N100N}: '
		else:
			instr = 'Outcome?: '
		outcome = input(instr).upper()
	else: # simulated version with fixed double letter handling
		outcome = ['N'] * 5
		secret_letters = list(secret)
		
		# First pass: mark correct positions (green)
		for idx, (cg, sg) in enumerate(zip(guess, secret)):
			if cg == sg:
				outcome[idx] = '1'
				secret_letters[idx] = None  # mark as used
		
		# Second pass: mark wrong positions (yellow)
		for idx, cg in enumerate(guess):
			if outcome[idx] == 'N' and cg in secret_letters:
				outcome[idx] = '0'
				secret_letters[secret_letters.index(cg)] = None  # mark as used
		
		outcome = ''.join(outcome)
		print('Outcome:',outcome)
		outcome = outcome.upper()
		
	if outcome=='11111':
			print('Congratulations! Score:',i+1)
			win = True
			break
		
	# trim possibilities
	for ig, (cg, og) in enumerate(zip(guess, outcome)):
		if og == 'N': # letter not in wordle
			if cg not in required:
				corpus = [w for w in corpus if cg not in w]
		elif og == '0': # letter elsewhere in wordle
			corpus = [w for w in corpus if w[ig]!=cg and cg in w]
			required += [cg]
		elif og == '1': # correct
			corpus = [w for w in corpus if w[ig]==cg]
			required += [cg]
	
	# describe possibilities
	print('Remaining corpus:',len(corpus),'words')
	print('Required:',''.join(set(required)).upper())
	optimalstring = ''.join([max(alphabet, key=[w[i] for w in corpus].count) for i in range(5)]).upper()
	print('Optimal placement:',optimalstring)
	optimallevenshtein = lambda w: edit_distance(w.lower(), optimalstring.lower())#, True)
	maxuniques = max([len(set(wi)) for wi in corpus])
	subcorpus = [w for w in corpus if len(set(w))==maxuniques]
	print('Recommended word:',min(corpus, key=optimallevenshtein).upper())
	print('Most useful word:',min(subcorpus, key=optimallevenshtein).upper())

	if len(corpus) < 50:
		print('Remaining wordspace:')
		print(corpus)

if not win:
	print('Sorry. Remaining wordspace was:')
	print(corpus)