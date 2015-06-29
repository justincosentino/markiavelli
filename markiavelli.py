"""
"""

# --------------------------------------------------------------------------- #

from classes.chain import MarkovChain
from classes.content import CommentContent, TextContent
from classes.reddit_interface import RedditInterface
import config
import praw
import random
import time

# --------------------------------------------------------------------------- #

# Wrapper for custom Markiavelli exceptions.
class MarkiavelliException(Exception):
	pass

# --------------------------------------------------------------------------- #

class Markiavelli(object):

	def __init__(self, username, password, user_agent, n=2, text_paths=[], db_paths=[]):
		"""
		"""
		# Save state
		print "Booting up `markiavelli`..."
		self.n = n
		self.text_paths = text_paths
		self.db_paths   = db_paths

		self.reddit_tool = RedditInterface(username, password, user_agent)

		# Initialize Content objects
		print "Building Content objects..."
		self.content = []
		for text_path in text_paths:
			self.content.append(TextContent(text_path))
		for db_path in db_paths:
			self.content.append(CommentContent(db_path))

		# Initialize Markov chain
		print "Initializing Markov chain..."
		self.mc = MarkovChain(self.content, self.n, [])

	def _get_keywords(self, comments):
		return []

	def _find_submission(self):
		"""
		"""
		return

	def _post(self, submission):
		"""
		"""
		# Use comments to generate context
		comments = self.reddit_tool.fetch_submission_comments_flat(submission)
		print "Markiavelli:: comment length: ", len(comments)
		keywords = self._get_keywords(comments)

		# Generate a new message and post it
		self.mc.update_context(keywords)
		msg = self.mc.generate_sentence()
		print submission
		print msg
		self.reddit_tool.post_comment(submission, msg)

	def monitor(self, subreddit, frequency):
		"""
		"""
		# submission_stream = praw.helpers.submission_stream(
		# 	self.reddit, 
		# 	subreddit,
		# 	limit=None,
		# 	verbosity=0
		# )
		# candidates = []
		# while True:
		# 	submission = next(submission_stream)
		# 	candidates.append(submission)
		# 	if len(candidates) == frequency:
		# 		submission = random.choice(candidates)
		# 		self._post(submission)
		# 		candidates = []
		# return
		print 'Monitoring r/%s...' % subreddit
		candidates = []
		while True:
			if len(candidates) >= frequency:
				submission = random.choice(candidates[:frequency])
				self._post(submission)
				candidates = candidates[frequency:]
				print 
			else:
				submissions = self.reddit_tool.fetch_submissions_controversial(
					subreddit
				)
				candidates.extend(submissions)
			print len(candidates)
			time.sleep(60*10)
		return

# --------------------------------------------------------------------------- #

def main():
	m = Markiavelli(
		config.username,
		config.password,
		config.user_agent,
		config.n,
		config.texts,
		config.dbs
	)
	m.monitor(config.subreddit, config.frequency)

# --------------------------------------------------------------------------- #

if __name__ == '__main__':
	main()

# --------------------------------------------------------------------------- #
