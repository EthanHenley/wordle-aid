import pickle
import os
from nltk import edit_distance
from random import choice

# Load corpus with caching
corpus_file = 'cache/wordle_corpus.pkl'

if os.path.exists(corpus_file):
    with open(corpus_file, 'rb') as f:
        raw_corpus = pickle.load(f)
else:
    from nltk.corpus import words
    raw_corpus = list(set([w.lower() for w in words.words() if len(w)==5]))
    with open(corpus_file, 'wb') as f:
        pickle.dump(raw_corpus, f)

convenience = {2:'1',1:'0',0:'N'}

# set mode
wtype = ''
while wtype == '':
	print('Word options: INPUT | RANDOM | LIVE')
	wtype = input('Word type?: ').upper()
	if wtype not in ('INPUT','RANDOM','LIVE'): wtype = ''

repeat = True
while repeat:
	alphabet = [chr(i) for i in range(ord('a'), ord('z')+1)]
	known_positions = {}  # position -> letter mapping for green letters
	letter_min_count = {}  # minimum count of each letter (from yellows/greens)
	letter_max_count = {}  # maximum count of each letter (from grays after yellows/greens)
	win = False
	live = False
	corpus = raw_corpus[:]

	if wtype == 'INPUT':
		secret = input('Input secret word: ').lower()
		secret = secret[:5]
	elif wtype == 'RANDOM':
		secret = choice(corpus)
	elif wtype == 'LIVE':
		live = True

	for i in range(6):
		# read guess, outcome
		if i==0:
			instr = 'Guess? F{EARTH}:   '
		else:
			instr = 'Guess?:            '
		guess = input(instr).lower()

		if live: # only input outcome codes if playing live game
			if i==0:
				instr = 'Outcome? F{N100N}: '
			else:
				instr = 'Outcome?:          '
			outcome = input(instr).upper()
		else: # simulated version with fixed double letter handling
			outcome = ['N'] * 5
			secret_letters = list(secret)
			
			# First pass: mark correct positions (green)
			for idx, (cg, sg) in enumerate(zip(guess, secret)):
				if cg == sg:
					outcome[idx] = '1'
					secret_letters[idx] = None  # mark position as used
			
			# Second pass: mark wrong positions (yellow)
			for idx, cg in enumerate(guess):
				if outcome[idx] == 'N':  # only check letters not already marked green
					# Check if this letter exists in remaining secret_letters
					if cg in secret_letters:
						outcome[idx] = '0'
						# Remove the FIRST occurrence of this letter
						secret_letters[secret_letters.index(cg)] = None
			
			outcome = ''.join(outcome)
			print('Outcome:          ',outcome)
			outcome = outcome.upper()
			
		if outcome=='11111':
				print('Congratulations! Score:',i+1)
				win = True
				break
		
		# Update letter counts based on this guess
		guess_letter_outcomes = {}  # letter -> list of outcomes for that letter
		for cg, og in zip(guess, outcome):
			if cg not in guess_letter_outcomes:
				guess_letter_outcomes[cg] = []
			guess_letter_outcomes[cg].append(og)
		
		for letter, outcomes in guess_letter_outcomes.items():
			green_count = outcomes.count('1')
			yellow_count = outcomes.count('0')
			gray_count = outcomes.count('N')
			
			total_present = green_count + yellow_count
			
			# Update minimum count (at least this many exist)
			if letter not in letter_min_count:
				letter_min_count[letter] = 0
			letter_min_count[letter] = max(letter_min_count[letter], total_present)
			
			# If we see grays after accounting for greens/yellows, set maximum
			if gray_count > 0 and total_present > 0:
				# We found some, but also got grays, so we know exact count
				letter_max_count[letter] = total_present
			elif gray_count > 0 and total_present == 0:
				# All grays means this letter doesn't exist at all
				letter_max_count[letter] = 0
			
		# Update known positions
		for ig, (cg, og) in enumerate(zip(guess, outcome)):
			if og == '1':
				known_positions[ig] = cg
			
		# Trim corpus based on all constraints
		new_corpus = []
		for word in corpus:
			valid = True
			
			# Check known positions (greens)
			for pos, letter in known_positions.items():
				if word[pos] != letter:
					valid = False
					break
			
			if not valid:
				continue
			
			# Check letter counts
			for letter, min_count in letter_min_count.items():
				if word.count(letter) < min_count:
					valid = False
					break
			
			if not valid:
				continue
			
			for letter, max_count in letter_max_count.items():
				if word.count(letter) > max_count:
					valid = False
					break
			
			if not valid:
				continue
			
			# Check yellow constraints (letter must exist but not in this position)
			for ig, (cg, og) in enumerate(zip(guess, outcome)):
				if og == '0' and word[ig] == cg:
					valid = False
					break
			
			if valid:
				new_corpus.append(word)
		
		corpus = new_corpus
		
		# describe possibilities
		print('Remaining corpus:',len(corpus),'words')
		required_letters = [k for k, v in letter_min_count.items() if v > 0]
		print('Required:',''.join(sorted(set(required_letters))).upper())
		
		if len(corpus) > 0:
			optimalstring = ''.join([max(alphabet, key=[w[i] for w in corpus].count) for i in range(5)]).upper()
			print('Optimal placement:',optimalstring)
			optimallevenshtein = lambda w: edit_distance(w.lower(), optimalstring.lower())
			maxuniques = max([len(set(wi)) for wi in corpus])
			subcorpus = [w for w in corpus if len(set(w))==maxuniques]
			print('Recommended word: ',min(corpus, key=optimallevenshtein).upper())
			print('Most useful word: ',min(subcorpus, key=optimallevenshtein).upper())

		if len(corpus) < 50:
			print('Remaining wordspace:')
			print(corpus)

	if not win:
		print('Sorry. Remaining wordspace was:')
		print(corpus)

	repeat = input('Repeat? [Y]/n: ').upper().strip() in ('Y','')