import pandas as pd

from profilescraper.profile import Profile
import requests
from bs4 import BeautifulSoup

class TestProfile:

    
    def test_from_soup(self):
        response = requests.get("https://twitter.com/elonmusk", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'})
        html = response.text

        soup = BeautifulSoup(html, "lxml")

        profile = Profile.from_soup(soup)
        assert(profile.username == "elonmusk")
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