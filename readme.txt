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


Configuration

$ cp config_clean.py config.py
$ $EDITOR config.py

The main point is the Twitter API key and OAuth secret -- here's 
how to obtain one:

  * Go to https://dev.twitter.com/
  * Sign in with your twitter account.
  * In the top right user menu, click on "My Applications".
  * Click on "Create a new application" and register an application.
  * When you're done with this, choose the "Settings" tab on the application's page.
  * Set the "Application type" to "Read"
  * Save setting by clicking "Update this Twitter application's settings"
  * Go to the "Details" tab of the application
  * Click "Create access token" and wait a while (some minutes or so).
  * Reload the "Details" tab
  * Copy and paste the access key data into the correct variables in your python file:
    * Consumer key        -> app_key
    * Consumer secret     -> app_secret
    * Access token        -> oauth_token
    * Access token secret -> oauth_token_secret
  * Re-check the key's access level below the token secret.

  
