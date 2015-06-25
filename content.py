"""
Class definitions for general Markov chain content storage objects. The Content
class provides an interface for the two children classes, CommentContent and 
TextContent. Each Content object reads from a content source and provides
methods for accessing ngrams, potential start states, and average sentence 
length.

Dependencies: nltk, sqlite
	  Author: Justin Cosentino
		Date: 06-25-2015
"""

# --------------------------------------------------------------------------- #

from collections import Counter
import nltk
import os
import re
import sqlite3

# --------------------------------------------------------------------------- #

# Wrapper for custom Content exceptions.
class ContentException(Exception):
	pass

# --------------------------------------------------------------------------- #

class Content(object):

	sentence_detector = nltk.data.load('tokenizers/punkt/english.pickle')

	def __init__(self, filepath, n=2):
		"""
		The Content wrapper parent class provides and interface for the 
		TextContent and CommentContent children classes to use. This class 
		itself should not be used. 
		"""
		# Init basic state
		self.filepath = filepath
		self.n = n
		self.total_length = 0.0
		self.total_sentences = 0.0

		
		# Perform computations on file load
		self.parsed_text = self._read_content()
		self.ngrams = self._extract_ngrams()
		self.start_states = self._extract_start_states()

	def _requires_file(self):
		"""
		Raises a custom ContentException if the provided input file does not
		exist.
		"""
		if not os.path.isfile(self.filepath):
			err = "Specified file does not exist: %s" % self.filepath
			raise ContentException(err)

	def _read_content(self):
		return

	def _extract_ngrams(self):
		"""
		Iterates over each block of text read in from `self._read_content()`. 
		Returns a list of lists, where each inner list contains ngram tuples
		from its associated block. Tuples are of the form:
				(prefix_1, prefix_2, ..., prefix_n, suffix)
		when n is the provided ngram length.
		"""
		ngrams = []
		for text_block in self.parsed_text:
			ngrams.append(nltk.util.ngrams(text_block.split(), self.n+1))
		return ngrams

	def _extract_start_states(self):
		"""
		Iterates over each block of text read in from `self._read_content()`.
		Tokenizes each block into sentences and considers all sentence starts
		of length at least n. These are returned as a Counter collection.
		"""
		start_states = []
		for text_block in self.parsed_text:
			
			# Tokenize text block into sentences
			sentences = self.sentence_detector.tokenize(text_block)
			
			# Update average sentence length accumulators
			self.total_sentences += len(sentences)
			self.total_length += sum(len(s.split()) for s in sentences)

			# Determine starting states
			starts = [tuple(s.split()[:self.n]) for s in sentences if len(s) >= self.n]
			start_states.extend(starts)

		counts = Counter(start_states)
		return counts

	def update_n(self, n):
		"""
		Update the ngram value and recalculate ngrams and start states.
		"""
		self.n = n
		self.ngrams = _extract_ngrams()
		self.start_states = self._extract_start_states()

	def get_ngrams(self):
		"""
		Return a list of lists. Each inner list contains the ngrams for the 
		associated text block.
		"""
		return self.ngrams

	def get_start_states(self):
		"""
		Return all start states using a Counter collection.
		"""
		return self.start_states

	def avg_sentence_len(self):
		"""
		Return the average length of a sentence from the text source as an 
		integer.
		"""
		return int(self.total_length / self.total_sentences)

# --------------------------------------------------------------------------- #s

class TextContent(Content):

	def __init__(self, filepath):
		"""
		TextContent takes a filepath to a text file on initialization and 
		parses this file, removing whitespace and newlines. ngrams, start 
		states, and average sentence length can then be retrieved with getter
		methods. 
		"""
		super(TextContent, self).__init__(filepath)

	def _read_content(self):
		"""
		Reads in content from a text file and removes all whitespace and newline
		characters from the string. Returns the contents of the file as a list 
		of a single string since the entire file is treated as a single block 
		of text.
		"""
		# Ensure file exists
		self._requires_file()

		# Open file and remove whitespace & newlines
		text = open(self.filepath).read()
		text = re.sub('\s+',' ',text).strip()
		return [text]

# --------------------------------------------------------------------------- #

class CommentContent(Content):

	def __init__(self, filepath):
		"""
		CommentContent takes a filepath to a sqlite db on initialization and 
		parses post bodies, removing whitespace and newlines. ngrams, start 
		states, and average sentence length can then be retrieved with getter
		methods. 
		"""
		super(CommentContent, self).__init__(filepath)

	def _read_content(self):
		"""
		Reads in content from the provided sqlite database. Removes all 
		whitespace and newline characters in addition to filtering out
		moderator auto-removal comments (TODO: remove from database). Returns
		a list of these comment strings, where each string represents a 
		distinct block of text.
		"""
		# Ensure file exists
		self._requires_file()

		# Open connection to database
  		conn = sqlite3.connect(self.filepath)
  		conn.text_factory = str
  		database = conn.cursor()

  		# Fetch all post bodies
  		cmd = "SELECT body FROM comments;"
  		res = database.execute(cmd)
  		res = res.fetchall()

  		# Filter out moderator comments and remove whitespace & newline chars
  		ignore_1 = "Thank you for participating in /r/Politics"
  		ignore_2 = "*I am a bot"
  		text = []
  		for r in res:
  			r_sub = re.sub('\s+',' ',r[0]).strip()
  			if ignore_1 in r_sub or ignore_2 in r_sub:
  				continue
  			else: 
  				text.append(r_sub)
  		return text

# --------------------------------------------------------------------------- #

def main():
	tc1 = TextContent("./texts/the_prince.txt")
	tc2 = TextContent("./texts/the_discourses.txt")
	cc  = CommentContent("./texts/rpolitics.db")	

# --------------------------------------------------------------------------- #

if __name__ == '__main__':
	main()

# --------------------------------------------------------------------------- #
