from profilescraper.query import query_single_profile, query_profile
import logging

def test_query_single_profile():
    profile = query_single_profile("https://twitter.com/elonmusk", logger=logging.getLogger())
    
    assert(profile.location == 0)
    assert(profile.has_location == 0)
    assert(profile.created == "2009-06-02")
    assert(profile.is_verified == 1)
    assert(int(profile.total_tweets) > 5000)
    assert(int(profile.total_following) > 20)
    assert(int(profile.total_followers) > 20000000)
    assert(int(profile.total_likes) > 1000)
    assert(int(profile.has_avatar) == 1)
    assert(int(profile.has_background) == 1)
    assert(int(profile.is_protected) == 0)
    assert(int(profile.profile_modified) == 1)
    assert(len(profile.tweets) >= 2)

def test_query_profiles():
    profileNames = ['realdonaldtrump', 'warproxxx', 'elonmusk']
    profiles = query_profile(profileNames, logger=logging.getLogger())

    for profile in profiles:
        if (profile.username == 'realDonaldTrump'):
            assert(profile.location == "Washington, DC")
            assert(profile.has_location == 1)
            assert(profile.created == "2009-03-18")
            assert(profile.is_verified == 1)
            assert(int(profile.total_tweets) > 5000)
            assert(int(profile.total_following) > 20)
            assert(int(profile.total_followers) > 40000000)
            assert(int(profile.total_likes) < 1000)
            assert(int(profile.has_avatar) == 1)
            assert(int(profile.has_background) == 1)
            assert(int(profile.is_protected) == 0)
            assert(int(profile.profile_modified) == 1)
            assert(len(profile.tweets) >= 2)
        elif (profile.username == "warproxxx"):
            assert(profile.location == 0)
            assert(profile.has_location == 0)
            assert(profile.created == "2017-04-11")
            assert(profile.is_verified == 0)
            assert(int(profile.total_tweets) < 5000)
            assert(int(profile.total_following) > 20)
            assert(int(profile.total_followers) < 20000000)
            assert(int(profile.total_likes) < 1000)
            assert(int(profile.has_avatar) == 0)
            assert(int(profile.has_background) == 0)
            assert(int(profile.is_protected) == 0)
            assert(int(profile.profile_modified) == 0)
            assert(len(profile.tweets) >= 2)
        else:
            assert(profile.location == 0)
            assert(profile.has_location == 0)
            assert(profile.created == "2009-06-02")
            assert(profile.is_verified == 1)
            assert(int(profile.total_tweets) > 5000)
            assert(int(profile.total_following) > 20)
            assert(int(profile.total_followers) > 20000000)
            assert(int(profile.total_likes) > 1000)
            assert(int(profile.has_avatar) == 1)
            assert(int(profile.has_background) == 1)
            assert(int(profile.is_protected) == 0)
            assert(int(profile.profile_modified) == 1)
            assert(len(profile.tweets) >= 2)