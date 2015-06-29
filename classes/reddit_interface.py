"""
"""

# --------------------------------------------------------------------------- #

from time import sleep
import praw

# --------------------------------------------------------------------------- #

# Wrapper for custom RedditInterface exceptions.
class RedditInterfaceException(Exception):
	pass

# --------------------------------------------------------------------------- #

class RedditInterface(object):

	def __init__(self, username, password, user_agent):
		"""
		"""
		# Init state
		self.num_comments = 0
		self.num_replies = 0	
		self.comment_ids = set()
		self.seen_submissions = set()
		self.seen_replies  = set()

		# Authenticate with Reddit
		self.reddit = self._login(username, password, user_agent)
		self.me = self.reddit.get_redditor(username)
		
	def _login(self, username, password, user_agent):
		"""
		"""
		reddit = praw.Reddit(user_agent)
		reddit.login(username, password)
		if not reddit.is_logged_in:
			raise MarkiavelliException("Invalid authentication credentials.")
		return reddit

	def _filter_seen_submissions(self, submissions):
		"""
		"""
		new_submissions = []
		for s in submissions:
			if s.fullname not in self.seen_submissions:
				new_submissions.append(s)
				self.seen_submissions.add(s.fullname)
		print "RedditInterface:: length: ", len(new_submissions)
		return new_submissions

	def fetch_submissions_controversial(self, subreddit, limit=None):
		"""
		"""
		submissions = self.reddit.get_subreddit(subreddit).get_controversial(limit=limit)
		return self._filter_seen_submissions(submissions)

	def fetch_submissions_hot(self, subreddit, limit=None):
		"""
		"""
		submissions = self.reddit.get_subreddit(subreddit).get_hot(limit=limit)
		return self._filter_seen_submissions(submissions)

	def fetch_submissions_new(self, subreddit, limit=None):
		"""
		"""
		submissions = self.reddit.get_subreddit(subreddit).get_top(limit=limit)
		return self._filter_seen_submissions(submissions)

	def fetch_submissions_rising(self, subreddit, limit=None):
		submissions = self.reddit.get_subreddit(subreddit).get_rising(limit=limit)
		return self._filter_seen_submissions(submissions)

	def fetch_replies_to_me(self):
		"""
		TODO: Fix this, it seems like get_comments does not provide replies.
		"""
		import pprint
		pp = pprint.PrettyPrinter(indent=4)
		my_comments = self.me.get_comments(sort='new', time=all)
		new_replies = []
		for comment in my_comments:
			pp.pprint(comment.__dict__)
			for reply in comment.replies:
				print reply
				if reply.fullname not in self.seen_replies:
					new_replies.append(reply)
					self.seen_replies.add(reply.fullname)
		return new_replies

	def fetch_submission_comments_flat(self, submission):
		"""
		"""
		return praw.helpers.flatten_tree(submission.comments)

	def post_comment(self, submission, msg):
		"""
		"""
		submission.add_comment(msg)
		self.num_comments += 1

	def post_reply(self, comment_id, msg):
		"""
		"""
		comment = self.reddit.get_info(thing_id=comment_id)
		comment.reply(msg)
		self.num_replies += 1

	def status(self):
		"""
		"""
		status = "RedditInterface:: Status: %d Comments; %d replies;" % (
			self.num_comments, 
			self.num_replies
		)
		print status

# --------------------------------------------------------------------------- #

def main():
	# TODO: Remove login credential
	user_agent = ''
	username   = '' 
	password   = ''

	ri = RedditInterface(user_agent, password, user_agent)


# --------------------------------------------------------------------------- #

if __name__ == '__main__':
	main()

# --------------------------------------------------------------------------- #
