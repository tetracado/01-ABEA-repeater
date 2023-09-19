import hidcpd001
import tweepy
import re
import time
import cpd001sel
import cpd001imgur
import cpd001abea
import schedule
import feedparser
#import os

def process_webpage(): #returns true if posted or false if not
    try:
        link="https://www.alberta.ca/alberta-emergency-alert.aspx"
        #getscreenshot
        retlink=cpd001abea.ab_getalertlink(link)
        print('retlink found:',retlink)
        if retlink==None:
            print('no new links found, exiting process_webage')
        else:
            cpd001sel.openlink(retlink)
            scrpath=cpd001sel.savescn(retlink)
            details=cpd001abea.ab_savedetails(retlink)
            imglink=cpd001imgur.postimg(scrpath)
            ptweettext="#ABemerg | "+details['alertsumm']+' '
            print('posting tweet: ',ptweettext)
            postid=posttweet(ptweettext+imglink)[0]['id']
            print('posted tweetid= ',postid)
            rep01text=details['description']
            print('posting:',rep01text)
            rep01id=postreply(rep01text,postid)[0]['id']
            rep02text=details['instructions']
            print('posting:', rep02text)
            rep02id=postreply(rep02text,rep01id)[0]['id']
            rep03text=details['link']
            print('posting:', rep03text)
            postreply(rep03text, rep02id)
            print('successfully posted thread, returning to listen cycle')
    except:
        print('failed to process webpage!!')


def rsschecker(url):
    try:
        feed=feedparser.parse(url)
        global globaletag
        if globaletag==feed.etag :
            print('same etag' + globaletag)
        else:
            print('new etag, pulling data' + feed.etag)
            process_webpage()
            globaletag=feed.etag
    except:
        print('failed to process rsschecker!!')

#def rsstester(etag, feed):
 #   global testetag
  #  if etag==feed.etag:
   #     print('same etag')
    #else:
    #    print('new etag')
     #   testetag=feed.etag 
   # print(testetag)

def posttweet(tweettext):
    postresponse=postclient.create_tweet(text=tweettext,user_auth=False)
    return(postresponse)

def postreply(tweettext,replyid):
    postresponse=postclient.create_tweet(in_reply_to_tweet_id=replyid,text=tweettext,user_auth=False)
    return(postresponse)

def startup():
    print(oauth2_user_handler.get_authorization_url())

    access_token=oauth2_user_handler.fetch_token(input("paste authorization response url: "))
    print("found access token: ",access_token)
    thisat=access_token['access_token']
    print('stored access token: ',thisat)
    thisrt=access_token['refresh_token']
    print('stored refresh token: ',thisrt)
    postclient=tweepy.Client(thisat, wait_on_rate_limit=True)
    return(thisat, thisrt, postclient)

def refreshcycle ():
    try:
        global thisrt
        global thisat
        global postclient
        cpd001sel.refreshcheck()
        print('refreshing token')
        newtokenresp=oauth2_user_handler.refresh_token('https://api.twitter.com/2/oauth2/token',refresh_token=thisrt)
        print('got token refresh response',newtokenresp)
        thisrt=newtokenresp['refresh_token']
        thisat=newtokenresp['access_token']
        print('stored access token: ',thisat)
        print('stored refresh token: ',thisrt)
        postclient=tweepy.Client(thisat, wait_on_rate_limit=True)
    except:
        print('failed to process refreshcycle!!')

oauth2_user_handler=tweepy.OAuth2UserHandler(
    client_id=hidcpd001.client_id2,
    redirect_uri=hidcpd001.redirect_uri,
    scope=["tweet.read","tweet.write","users.read","offline.access"],
    client_secret=hidcpd001.client_secret2
    )

(thisat, thisrt, postclient)=startup()
#globalfeed=feedparser.parse('https://www.alberta.ca/data/aea/rss/feed-full.atom')
globaletag="defaultetag"

#testfeed=feedparser.parse('find a rss feed herethat uses etggg')
#testetag=testfeed.etag

schedule.every(2).minutes.do(rsschecker, url="https://www.alberta.ca/data/aea/rss/feed-full.atom")
schedule.every(15).minutes.do(process_webpage) #make this part only happen in new etag but no new post
schedule.every(90).minutes.do(refreshcycle)

while True:
    schedule.run_pending()
    time.sleep(1)