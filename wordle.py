from nltk.corpus import words
from nltk import edit_distance
from random import choice

corpus = [w.lower() for w in words.words() if len(w)==5]
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
		outcome = input(instr).lower()
	else: # simulated, slightly broken version
		outcome = ''
		for (cga, sga) in zip(guess, secret):
			outcome += convenience[int((cga==sga)+(cga in secret))] # slight error with how this handles double letters
		print('Outcome:',outcome)
		outcome = outcome.lower()
	if outcome=='11111':
			print('Congratulations! Score:',i+1)
			win = True
			break
		
	# trim possibilities
	for ig, (cg, og) in enumerate(zip(guess, outcome)):
		if og == 'n': # letter not in wordle
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
	print('Recommended word:',min(corpus, key=optimallevenshtein).upper())

	if len(corpus) < 50:
		print('Remaining wordspace:')
		print(corpus)

if not win:
	print('Sorry. Remaining wordspace was:')
	print(corpus)