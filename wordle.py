from nltk.corpus import words
from nltk import edit_distance

corpus = [w.lower() for w in words.words() if len(w)==5]
alphabet = [chr(i) for i in range(ord('a'), ord('z')+1)]
required = []
win = False

for i in range(6):
	# read guess, outcome
	if i==0:
		instr = 'Guess? F{EARTH}:'
	else:
		instr = 'Guess?:'
	guess = input(instr).lower()

	if i==0:
		instr = 'Outcome? F{N100N}:'
	else:
		instr = 'Outcome?:'
	outcome = input(instr).lower()

	if outcome=='11111':
		print('Congratulations!')
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
	optimallevenshtein = lambda w: edit_distance(w, optimalstring)#, True)
	print('Recommended word:',max(corpus, key=optimallevenshtein).upper())

	if len(corpus) < 50:
		print('Remaining wordspace:')
		print(corpus)

if not win:
	print('Sorry. Remaining wordspace was:')
	print(corpus)