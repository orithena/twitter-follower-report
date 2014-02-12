import twython
import config
from time import time
import redis
import smtplib
from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

r = redis.StrictRedis(host=config.REDIS_SERVER, port=config.REDIS_PORT, db=config.REDIS_DB)
twitter = twython.Twython(app_key=config.TWITTER_CONSUMER_KEY, app_secret=config.TWITTER_CONSUMER_SECRET, oauth_token=config.TWITTER_ACCESS_TOKEN, oauth_token_secret=config.TWITTER_TOKEN_SECRET)

body = []

def sendemail(data):
                outer = MIMEMultipart()
                outer['Subject'] = data['subject']
                outer['From'] = data['from']
                outer['To'] = data['to']
                outer.preamble = ''
                text = MIMEText( data['text'], 'plain', 'utf-8')
                outer.attach(text)
                s = smtplib.SMTP(config.SMTP_SERVER)
                s.ehlo()
                s.starttls()
                s.ehlo()
                if config.SMTP_USERNAME:
                    s.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
                s.sendmail(data['from'], [data['to']], outer.as_string())
                s.quit()
                
def main():
    # retreive followers
    #   returns a dict formatted from the JSON data returned

    compare('followers')
    compare('friends')
    
    followers = r.zrevrange('followers', 0, -1)
    friends = r.zrevrange('friends', 0, -1)
    body.append('*** People not following you back ***')
    body.append('')
    add_details_to_report(list(set(friends) - set(followers)))
    body.append('*** People you don\'t follow back ***')
    body.append('')
    add_details_to_report(list(set(followers) - set(friends)))

    # send email report
    data = {
        'to': config.TO_ADDRESS,
        'from': config.FROM_ADDRESS,
        'subject': 'Twitter follower report',
        'text': '\n'.join(body)
    }
    print 'mailing...'
    print '\n'.join(body)
    sendemail(data)

def compare_lists():
    followers = r.zrevrange('followers', 0, -1)
    friends = r.zrevrange('friends', 0, -1)
    body.append('*** People not following you back ***')
    body.append('')
    print 'finding friends that do not follow you'
    add_details_to_report(list(set(friends) - set(followers)))
    body.append('*** People you don\'t follow back ***')
    body.append('')
    print 'finding followers you do not follow'
    add_details_to_report(list(set(followers) - set(friends)))

def compare(group):
    ids = []
    print 'getting twitter %s ids 5000 at a time' % group
    cursor = -1;
    while cursor != 0:
        apiData = twitter.get_followers_ids(cursor=cursor) if group == 'followers' else twitter.get_friends_ids(cursor=cursor)
        print 'retrieved (next): %s (%s)' % (len(apiData['ids']), apiData['next_cursor'])

        ids.extend(apiData['ids'])
        cursor = apiData['next_cursor']

    print 'retrieved total %s: %s' % (group, len(ids))

    # update entries in db but not follower list as unfollowed
    existing = r.zrevrange(group, 0, -1) or []
    print '%s in database: %s' % (group, len(existing))
    print 'checking for subtractions'
    unfollow_ids = []
    follow_ids = []

    for uid in existing:
        if long(uid) in ids: continue

        # update item
        print 'subtracted: %s' % uid
        unfollow_ids.append(uid)
        r.zrem(group, uid)

    # create new entries if they don't exist
    print 'checking for additions'
    for uid in ids:
        if (r.zscore(group, uid) or None != None):
            continue
        print 'added: %s' % uid
        follow_ids.append(uid)
        r.zadd(group, time(), uid)

    # create email body
    body.append('*** (%s) Unfollows ***' % group)
    body.append('')

    # look up info for unfollows
    if unfollow_ids:
        add_details_to_report(unfollow_ids)

    body.append('*** (%s) Follows ***' % group)
    body.append('')

    if follow_ids:
        add_details_to_report(follow_ids)

    #print '\n'.join(body)

def add_details_to_report(user_ids):
    for ids in chunker(user_ids, 100):
        user_ids_string = ','.join(map(str, ids))
        #print user_ids_string
        apiData = twitter.lookup_user(user_id=user_ids_string)

        for user in apiData:
            body.append(u'%s (%s)' % (user['screen_name'], user['name']))
            body.append(u'https://twitter.com/%s' % user['screen_name'])
            body.append(unicode(user['description']))
            body.append('')

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

if __name__ == '__main__':
    main()
