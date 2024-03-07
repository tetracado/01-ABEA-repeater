import hidcpd001
import tweepy
import re
import time
import cpd001sel
import cpd001imgur
import cpd001abea
import schedule
import feedparser
import typing as t
from atproto import Client, models,client_utils
#import os

#There have been so many alerts today that this bot has been rate limited. Please direct all complaints towards Twitter's API limits for free accounts. The bot will resume posting when possible - please follow @AB_EmergAlert and https://alberta.ca/alberta-emergency-alert.aspx for the latest information.

totaltweets=0 #as of september 1, grand total 1650

def extract_url_byte_positions(text: str, *, encoding: str = 'UTF-8') -> t.List[t.Tuple[str, int, int]]:
    """This function will detect any links beginning with http or https."""
    #https://github.com/MarshalX/atproto/blob/main/examples/advanced_usage/auto_hyperlinks.py
    encoded_text = text.encode(encoding)

    # Adjusted URL matching pattern
    pattern = rb'https?://[^ \n\r\t]*'

    matches = re.finditer(pattern, encoded_text)
    url_byte_positions = []

    for match in matches:
        url_bytes = match.group(0)
        url = url_bytes.decode(encoding)
        url_byte_positions.append((url, match.start(), match.end()))

    return url_byte_positions

def injecturls(text: str):

    url_positions = extract_url_byte_positions(text)
    facets = []

    for link_data in url_positions:
        uri, byte_start, byte_end = link_data
        facets.append(
            models.AppBskyRichtextFacet.Main(
                features=[models.AppBskyRichtextFacet.Link(uri=uri)],
                index=models.AppBskyRichtextFacet.ByteSlice(byte_start=byte_start, byte_end=byte_end),
            )
        )
    return facets


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
                #raise Exception("forced error to skip tweetposting")
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
            except Exception as errortext:
                print('failed to post twitter thread with error',errortext) 
            #bskypostinghere     
            try:
               # raise Exception("forced error to skip bskyposting")
                alertsumm=details['alertsumm'][8:]   #removing    {#ABemerg}
                description=details['description']+" "+ rsclink
                instructions=details['instructions']
                linkstr=details['link']
                root_post_ref=models.create_strong_ref(bskyclient.send_image(text=client_utils.TextBuilder().tag('#ABemerg','ABemerg').text(alertsumm),facets=injecturls(alertsumm),image=open(scrpath,'rb'),image_alt='Screenshot of alert'))
                reply_to_ref0=models.create_strong_ref(bskyclient.send_post(text=description,facets=injecturls(description),reply_to=models.AppBskyFeedPost.ReplyRef(parent=root_post_ref,root=root_post_ref)))
                reply_to_ref1=models.create_strong_ref(bskyclient.send_post(text=instructions,facets=injecturls(instructions),reply_to=models.AppBskyFeedPost.ReplyRef(parent=reply_to_ref0,root=root_post_ref)))
                reply_to_ref2=models.create_strong_ref(bskyclient.send_post(text=linkstr,facets=injecturls(linkstr),reply_to=models.AppBskyFeedPost.ReplyRef(parent=reply_to_ref1,root=root_post_ref)))
                print('successfully posted bsky thread, returning to listen cycle')
                #myimage=open('unknow1n.png','rb')
                #print('loaded image')
                #print(bskyclient.send_image(text='textimage',image=myimage,image_alt='myimagealt'))
            except Exception as errortext:
                print('failed to post bskythread thread with error',errortext) 
           
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

rsschecker("https://www.alberta.ca/data/aea/rss/feed-full.atom")

schedule.every(2).minutes.do(rsschecker, url="https://www.alberta.ca/data/aea/rss/feed-full.atom")
schedule.every(15).minutes.do(process_webpage) 
schedule.every(90).minutes.do(refreshcycle)

while True:
    schedule.run_pending()
    time.sleep(1)