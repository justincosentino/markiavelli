"""
"""

# --------------------------------------------------------------------------- #

from collections import defaultdict, Counter
import copy
import random
import re

# --------------------------------------------------------------------------- #

# Wrapper for custom MarkovChain exceptions.
class MarkovChainException(Exception):
	pass

# --------------------------------------------------------------------------- #

class MarkovChain(object):

	def __init__(self, content, n=2, context=[]):
		"""
		content: list, list of TextContent and CommentComment objects
		ngrams:  int,  prefix length
		context: list, list of strings where each string is a keyword
		"""
		
		self.content_objs = content
		self.context_keywords = {k: True for k in context}
		self.n = n

		self.transitions = self._read_from_content()
		self.weighted_transitions = self._analyze_context()
		self.start_states = self._get_start_states()

	def _read_from_content(self):
		"""
		Interfaces with Content objects to pull ngrams and generate transition
		probabilities. Returns context-unaware transition probabilities.
		"""
		# Fetch all ngrams
		transitions = defaultdict(list)
		for content in self.content_objs:
			for ngram_block in content.get_ngram_blocks():
				for ngram in ngram_block:
					prefix = ngram[:self.n]
					suffix = ngram[-1]
					transitions[prefix].append(suffix)
		return transitions 

	def _analyze_context(self, weight=2):
		"""
		If a list of context strings are provided, increase the probability
		of transitioning to a state containing a context word by {weight},
		where {weight} is multiplied by the number of occurrences.

		weight: int, value by which to multiple the number of occurrences of 
				context words
		"""
		# If no provided context, apply no weighting
		if not self.context_keywords:
			return self.transitions

		# TODO: this seems bad, but I need to determine how 
		# often context will change (lots = keep a local copy)
		# of original transitions, little = overwrite then re-read)
		context_transistions = copy.deepcopy(self.transitions)

		# Apply weight to each occurrence of a context word
		for t in context_transistions:
			# Cast each list of possible suffixes to a Counter collection
			counter = Counter(context_transistions[t])
			for suffix in counter:
				if suffix in self.context_keywords:
					counter[suffix] *= weight
			context_transistions[t] = list(counter.elements())
		print context_transistions
		return context_transistions

	def _get_start_states(self, weight=2):
		"""
		"""
		start_states = Counter() 
		for c in self.content_objs:
			start_states += c.get_start_states()
		if self.context_keywords:
			for state in start_states:
				for word in state:
					if word in self.context_keywords:
						start_states[state] *= weight
		return list(start_states.elements())

	def _select_start_state(self):
		"""
		Randomly select and return a start start.
		"""
		return random.choice(self.start_states)

	def _valid_start_state(self, start):
		"""
		Given a start state, validate that it is the proper length. Raise a
		MarkovChainException if not. If no start state is given, generate one.

		start: str, proposed start state
		"""
		# If no start state given, generate one
		if not start:
			return self._select_start_state()
		
		# Ensure given start state is of the correct length
		start = start.strip().split()
		if len(start) < self.n:
			raise MarkovChainException("Provided start state is too short.")
		return start

	def _is_ending(self, chain):
		exceptions = "U.S.|U.N.|E.U.|F.B.I.|C.I.A.".split("|")
		if chain[-1] in exceptions:
			return False
		if chain[-1][-1] in ["?", "!"]:
			return True
		if len(re.sub(r"[^A-Z]", "", chain[-1])) > 1:
			return True
		if chain[-1][-1] == ".":
			return True
		return False

	def _step(self, chain):
		"""
		"""
		# Fetch current prefix
		prefix = tuple(chain[-self.n:])

		# Ensure prefix is valid
		if not self.weighted_transitions[prefix]:
			err = "%s: not a valid prefix." % str(prefix)
			raise MarkovChainException(err)

		# Randomly select prefix
		suffix = random.choice(self.weighted_transitions[prefix])
		return suffix

	def generate_sentence(self, start='', min_length=20, length_error=5):
		"""
		min_length: int, the desired length of the generated sentence
		length_error: int, error margin for generated sentence
		"""
		chain = list(self._valid_start_state(start))
		while True:
			try:
				chain.append(self._step(chain))
			except MarkovChainException as e:
				break

			if len(chain) > min_length and self._is_ending(chain):
				break

		return ' '.join(chain)

	def generate_short_sentence(self, start='', chars=140):
		"""
		chars: int, character limit for generated sentence
		"""
		# TODO: complete
		return

	def update_ngram_size(self, n):
		"""
		n: int, new length of prefix ngrams
		"""
		self.n = n
		self.transitions = self._read_from_content()
		self.weighted_transitions = self._analyze_context()
		self.start_states = self._get_start_states()

	def update_context(self, context):
		"""
		context: list, list of strings representing new context keywords
		"""
		self.context_keywords = {k: True for k in context}
		self.weighted_transitions = self._analyze_context()
		self.start_states = self._get_start_states()

# --------------------------------------------------------------------------- #

def main():
	from content import TextContent, CommentContent

	n   = 3
	tc1 = TextContent("./texts/the_prince.txt", n)
	tc2 = TextContent("./texts/the_discourses.txt", n)
	cc  = CommentContent("./texts/rpolitics.db", n)

	content = [tc1, tc2, cc]
	mc = MarkovChain(content, n, [])
	for i in range(10):	
		print mc.generate_sentence()
		print 


# --------------------------------------------------------------------------- #

if __name__ == '__main__':
	main()

# --------------------------------------------------------------------------- #
