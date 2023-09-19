import hidtet
import tweepy

oauth2_user_handler = tweepy.OAuth2UserHandler(
    client_id=hidtet.client_id,
    redirect_uri=hidtet.redirect_uri,
    scope=["tweet.read", "users.read", "tweet.write"],
    # Client Secret is only necessary if using a confidential client
    client_secret=hidtet.client_secret
)

print(oauth2_user_handler.get_authorization_url())

authorization_response=input("paste url here: ")

access_token = oauth2_user_handler.fetch_token(authorization_response)

user_access_token=access_token["access_token"]
print('user access token is',user_access_token)
