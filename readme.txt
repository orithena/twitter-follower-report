Script to track Twitter followers/unfollowers with email report. Uses Redis
as data store.

To use:
- Rename config_clean.py to config.py and populate with your credentials.
- Run python twitter-follower-report.py

Original write up: http://john-sheehan.com/post/16361552832/first-impressions-of-dynamodb

First version by John Sheenan (https://github.com/johnsheehan).
This version is heavily rewritten by Dave Kliczbor (https://github.com/orithena/twitter-follower-report).

Differences between Johns and Daves version:
	* Dropped SendGrid support
	* Switched to Twython as twitter lib
	* Added plain old SMTP
	* Added "People not following you back" category
	* Added "People you don't follow back" category

	