import traceback
import time
import praw
import sqlite3
import re

def scanSub():
	'''
	Scans given subreddit
	Posts if post does not exist in db
	'''
    print('Scanning for jokes on /r/' + redditsub + '.')
    subreddit = r.get_subreddit(redditsub)
    posts = subreddit.get_comments(limit = maxposts)
    for post in posts:
        pid = post.id 
        try:
            postauthor = post.author.name
            cur.execute('SELECT * FROM oldposts WHERE ID=?', [pid])
            if not cur.fetchone():
                pbody = post.body.lower()
                match = re.search(find_exp, pbody, re.IGNORECASE)
                notmatch = re.search(bad_exp, pbody, re.IGNORECASE)
                subredditbans = re.search(subreddit_exp, pbody, re.IGNORECASE)
                if match and not notmatch and not subredditbans and postauthor.lower() != username.lower() and not postauthor.lower() in dontreplytome.lower:
                    print('Found one! Replying to ' + pid + ' by ' + postauthor)
                    post.reply(reply)
                    print('Successfully commented')
                else:
                    print('No posts or will not reply to self or replied to comment')
                cur.execute('INSERT INTO oldposts Values(?)', [pid])
        except praw.errors.APIException:
            if exception.error_type in ('TOO_OLD','DELETED_LINK'):
                cur.execute('INSERT INTO oldposts Values(?)', [pid])
                print("Can't post comment: archived by reddit")
        except AttributeError:
            print("Deleted post lol!")
            #Deleted posts lol!
            pass
    sql.commit()

#USERNAME FOR BOT ACCOUNT HERE
username = ""
#INSERT USERNAMES FOR YOUR SOMEONE YOU DONT WANT TO REPLY TO HERE
dontreplytome = ["Mattophobia"]
#PASSWORD FOR BOT ACCOUNT HERE
password = "" 
#REQUIRED FOR REDDIT NOT TO BAN YOUR SODDING ACCOUNT.
useragent = "!CHANGE THIS BEFORE RUNNING!"
#THIS SUBREDDIT THAT THIS IS USED ON
redditsub = "nerdcubed" 
#REGEX TO FIND JOKES
find_exp = r'(he|dan|nerd).{1,15}?(banned from)'
#IF IT MATCHES THID DON'T REPLY
bad_exp = r'many.{1,15}?places'
subreddit_exp = r'th.{1,3}?sub.{0,8}?'
#WHAT THE BOT REPLIES WITH
reply = "He's banned from many places"
#THE MAXIMUM AMOUNT OF POSTS FETCHED AT ONCE
maxposts = 100


#CREATE DB CONNECTION
sql = sqlite3.connect('sql.db')
print('Loaded SQL Database')
cur = sql.cursor()

#SET-UP TABLES
cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)')
print('Loaded old post table')

sql.commit()

#LOGIN TO REDDIT
print('Logging in to reddit...')
r = praw.Reddit(useragent)
r.login(username, password)


while True:
    try:
        scanSub()
    except Exception as e:
        traceback.print_exc()
    print('Running again in %d seconds \n' % wait)
    sql.commit()