from profilescraper.query import query_single_profile, query_profile

# def test_query_single_page():
#     tweets, ids = query_single_page("https://twitter.com/search?vertical=tweets&vertical=default&q=Bitcoin&l=EN")
    
#     for tweet in tweets:
#         assert(int(tweet.retweets) >= 0)

# def test_query_tweets():
#     tweets = query_tweets("Bitcoin", limit=50)

#     assert(len(tweets) > 50)

#     for tweet in tweets:
#         assert(int(tweet.replies) >= 0)