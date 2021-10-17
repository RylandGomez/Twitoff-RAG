import tweepy
import os


def get_user_info(screen_name):
    # First, get API authentication and object
    os.getenv("TWITTER_API_SECRET_KEY")
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET_KEY = os.getenv("TWITTER_API_SECRET_KEY")

    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET_KEY)
    twitter = tweepy.API(auth)

    #Then, populate python objects
    user = twitter.get_user(screen_name=screen_name)
    screen_name = user.screen_name
    user_id = user.id

    # Return objects
    return user_id, screen_name

def get_tweets(user_id):
    # Establish API connection
    os.getenv("TWITTER_API_SECRET_KEY")
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET_KEY = os.getenv("TWITTER_API_SECRET_KEY")

    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET_KEY)
    twitter = tweepy.API(auth)

    # Retrieve user class
    user = twitter.get_user(user_id=user_id)
    # Recover originally created tweets out of last 200
    user_tweets = user.timeline(
        count=200,
        exclude_replies=True,
        include_rts=False,
        tweet_mode="Extended"
    )
    # Create list of dicts of pertinent data
    tweet_dict = []
    for i in user_tweets:
        tweet_dict.append({'tweet_id':i.id, 'tweet_text':i.text})

    # Return dictionaries
    return tweet_dict

