import hidcpd001
import tweepy
import re
import time
import cpd001sel
import cpd001imgur
import cpd001abea
import schedule
import feedparser
from atproto import Client, models
#import os

#There have been so many alerts today that this bot has been rate limited. Please direct all complaints towards Twitter's API limits for free accounts. The bot will resume posting when possible - please follow @AB_EmergAlert and https://alberta.ca/alberta-emergency-alert.aspx for the latest information.

totaltweets=0 #as of september 1, grand total 1650

def process_webpage(): #returns true if posted or false if not
    global totaltweets
    tweetlimitchecker(totaltweets)
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
            try:
                rsclink=cpd001imgur.postimg(details['rsclink'])
            except:
                print('couldnt find resource to post to imgur, skipping and subbing blank')
                rsclink=""
            #twitter posting here
            try:
                ptweettext=details['alertsumm']
                print('posting tweet: ',ptweettext) #summary
                postid=posttweet(ptweettext+' ' +imglink)[0]['id']
                print('posted tweetid= ',postid)
                #rep00text=details['area']
                #print('posting:',rep00text)
                #rep00id=postreply(rep00text,postid)[0]['id']
                rep00text=details['description'] + " " + rsclink
                print('posting:',rep00text)
                rep00id=postreply(rep00text,postid)[0]['id']
                rep01text=details['instructions']
                print('posting:', rep01text)
                rep01id=postreply(rep01text,rep00id)[0]['id']
                rep02text=details['link']
                print('posting:', rep02text)
                postreply(rep02text, rep01id)
                totaltweets=totaltweets+4
                print('total tweets is',totaltweets)
                print('successfully posted twitter thread, returning to listen cycle')
            except:
                print('failed to post twitter thread')  
            #bskypostinghere     
            try:
                #bskyclient._refresh_and_set_session()
                root_post_ref=models.create_strong_ref(bskyclient.send_image(text=details['alertsumm'],image=open(scrpath,'rb'),image_alt='Screenshot of alert'))
                reply_to_ref0=models.create_strong_ref(bskyclient.send_post(text=details['description'] + " " + rsclink,reply_to=models.AppBskyFeedPost.ReplyRef(parent=root_post_ref,root=root_post_ref)))
                reply_to_ref1=models.create_strong_ref(bskyclient.send_post(text=details['instructions'],reply_to=models.AppBskyFeedPost.ReplyRef(parent=reply_to_ref0,root=root_post_ref)))
                reply_to_ref2=models.create_strong_ref(bskyclient.send_post(text=details['link'],reply_to=models.AppBskyFeedPost.ReplyRef(parent=reply_to_ref1,root=root_post_ref)))
                print('successfully posted bsky thread, returning to listen cycle')
                #myimage=open('unknow1n.png','rb')
                #print('loaded image')
                #print(bskyclient.send_image(text='textimage',image=myimage,image_alt='myimagealt'))
            except:
                print('failed to post bsky thread')
           
    except Exception as errortext:
        print('failed to process webpage!! with error',errortext)

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
    except Exception as errortext:
        print('failed to process rsschecker!! with error',errortext)

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
    except Exception as errortext:
        print('failed to process refreshcycle!!with error',errortext)

oauth2_user_handler=tweepy.OAuth2UserHandler(
    client_id=hidcpd001.client_id,
    redirect_uri=hidcpd001.redirect_uri,
    scope=["tweet.read","tweet.write","users.read","offline.access"],
    client_secret=hidcpd001.client_secret
    )

(thisat, thisrt, postclient)=startup()
#globalfeed=feedparser.parse('https://www.alberta.ca/data/aea/rss/feed-full.atom')
globaletag="defaultetag"

#testfeed=feedparser.parse('find a rss feed herethat uses etggg')
#testetag=testfeed.etag

transfertext="Due to Twitter's 1500 tweet limit for free apps, this account will soon be limited from posting tweets until the month is over. Follow @ABEA_repeater2 for updates through the rest of the month. This tweet will be deleted once posting resumes."

def tweetlimitchecker(tweetcount):
    if tweetcount>1450:
        postid=posttweet(transfertext)
        print('posted tweetid= ',postid)
        rep01text="Ping @tetracado"
        postreply(rep01text,postid)

#process_webpage()

bskyclient=Client()
bskyclient.login('abalertrepeater.bsky.social',hidcpd001.bskykey)
print('logged in to bsky')

schedule.every(2).minutes.do(rsschecker, url="https://www.alberta.ca/data/aea/rss/feed-full.atom")
schedule.every(15).minutes.do(process_webpage) 
schedule.every(90).minutes.do(refreshcycle)

while True:
    schedule.run_pending()
    time.sleep(1)