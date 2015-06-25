"""
Class definition for a Reddit CommentScraper object. Provides various methods
for fetching comments from a given subreddit and then writes them to an sqlite
database.

Dependencies: praw, sqlite
	  Author: Justin Cosentino
		Date: 06-25-2015
"""

# --------------------------------------------------------------------------- #

from time import sleep
import os
import praw
import sqlite3

# --------------------------------------------------------------------------- #

# Wrapper for custom CommentScraper exceptions.
class CommentScraperException(Exception):	
    pass

# --------------------------------------------------------------------------- #

class CommentScraper(object):

	def __init__(self, subreddit, database_path):
		"""
		CommentScraper connects to an sqlite database, fetches comments from
		a designated subreddit using PRAW, and writes those comments to those
		database. Note: if the designated database path does not exist, a new
		sqlte database will be created.

		subreddit: string, name of subreddit (eg. politics)
		database_path: string, desired path to sqlite database 
		"""
		self.subreddit = subreddit

		# Init database
		self.conn = None
		self.database = None
		self.database_path = database_path
		self._connect_database()

		# Init Reddit session
		user_agent  = "python:markiavelli:v0.0.1 (by @c0sentin0)"
		self.reddit = praw.Reddit(user_agent=user_agent)
		self.subreddit_instance = self.reddit.get_subreddit(self.subreddit)

		self.num_records = self._get_num_records()
		self.num_added = 0


	def _connect_database(self):
		"""
		Connects to a preexisting sqlite database or generates a new database
		and initializes the `comments` table.
		"""
		if not self.database_path:
			self.database_path = '%s_comments.db' % subreddit

		# Determine if tables must be created
		db_exists = os.path.isfile(self.database_path)

		# Open connection to database
  		self.conn = sqlite3.connect(self.database_path)
  		self.conn.text_factory = str
  		self.database = self.conn.cursor()

  		if not db_exists:
  			self._create_tables()


  	def requires_db(self):
  		"""
  		Raises a CommentScraperException if the CommentScraper does not have
  		a connection to the sqlite database.
  		"""
  		if self.database is None or self.conn is None:
			raise CommentScraperException("No sqlite database connection.")


	def _create_tables(self):
		"""
		Creates a `comments` table in the sqlite database. Requires a 
		connection to the database.
		"""
		cmd = """CREATE TABLE comments
                 (id text, author text, body text, time real, PRIMARY KEY (id))"""
		self.database.execute(cmd)


	def _insert(self, parsed_comments):
		"""
		Given a list of `comment` tuples of the form (reddit_fullname_id, 
		author_name, post_body, time_stamp), insert these values into the
		database. Duplicate values are ignored, allowing for new values to 
		be inserted into the database in bulk. Requires a connection to the
		database.

		parsed_comments: list, contains `comment` tuples
		"""
		self.requires_db()
		cmd = "INSERT OR IGNORE INTO comments VALUES (?,?,?,?)"
		self.database.executemany(cmd, parsed_comments)
		self.conn.commit()
		self._update_num_records()


	def _get_num_records(self):
		"""
		Returns the number of records in the given database. Requires a 
		connection to the database.
		"""
		self.requires_db()
		cmd = "SELECT count(id) FROM comments"
		res = self.database.execute(cmd)
		res = res.fetchone()
		return res[0]

	
	def _update_num_records(self):
		"""
		Updates the count of the number of new records that have been added to
		the database.
		"""
		new_num_records = self._get_num_records()
		self.num_added += new_num_records - self.num_records
		self.num_records = new_num_records

	
	def _status(self):
		"""
		Prints the status of the CommentScraper.
		"""
		print "CommentScraper: A total of %d records have been added to %s." % (self.num_added, self.database_path)


	def close(self, updates=False):
		"""
		Close the connection to the database. This should only be called 
		when you are done using the CommentScraper. Requires a connection
		to the database.

		updates: bool, to print periodic updates
		"""
		self.requires_db()
		self.conn.close()
		if updates: 
			print "CommentScraper: Connection to %s closed." % self.database_path
			self._status()


  	def scrape(self):
  		"""
  		Connects to Reddit using PRAW and gets the 1,000 most recent comments 
  		from the designated subreddit. This comments are then written and 
  		committed to the sqlite database. Duplicates are ignored in this phase
  		as the database insert accounts for them. Requires a connection to the
  		database.
  		"""
  		# Fetch last 1000 comments (Reddit API limit)
  		parsed_comments = []
  		subreddit_comments = self.subreddit_instance.get_comments(limit=None)	
		for c in subreddit_comments:
			parsed_c = (c.fullname, str(c.author), c.body, c.created)
			parsed_comments.append(parsed_c)

		# Insert comments, commit to database, and close sqlite connection
		self._insert(parsed_comments)


	def scrape_interval(self, num_times, interval=60, updates=False):
		"""
		Fetch the most recent 1,000 comments from the subreddit a given number
		of times, waiting a given number of seconds in between.

		num_times: int, the number of times to poll the subreddit for new 
				   comments
		interval: int, the time, in seconds, to wait between polls
		updates: bool, to print periodic updates
		"""
		for i in xrange(num_times):
			self.scrape()
			if updates: self._status()
			sleep(interval)


	def monitor(self, limit=100000, interval=60, updates=False):
		"""
		Monitor a PRAW stream for new comments within the given subreddit. Will
		continue to add records to the sqlite database until the provided limit
		has been reached.

		limit: int, the max number of comments to scrape
		wait: int, the time to wait before .comment_stream requests
		updates: bool, to print periodic updates
		"""
		# TODO: This function
		while self.num_added < limit:
			parsed_comments = []

			# Monitor the given subreddit and scrape comments
			subreddit_comments = praw.helpers.comment_stream(
				self.reddit, 
				self.subreddit, 
				limit=None)
			for c in subreddit_comments:
				parsed_c = (c.fullname, str(c.author), c.body, c.created)
				parsed_comments.append(parsed_c)
			
			# Insert comments and wait
			self._insert(parsed_comments)
			if updates: self._status()
			sleep(interval)

# --------------------------------------------------------------------------- #

def main():
	# Init a comment scraper
	cs = CommentScraper("politics", "./texts/rpolitics.db")
	
	# Check for more comments every 10 minutes
	wait = 10 * 60
	cs.scrape_interval(10, wait, True)
	# cs.monitor(100, wait, True)

	# Close the database connection
	cs.close(True)

# --------------------------------------------------------------------------- #

if __name__ == "__main__":
	main()

# --------------------------------------------------------------------------- #
