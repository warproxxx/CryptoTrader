from datetime import datetime
from bs4 import BeautifulSoup

from coala_utils.decorators import generate_ordering
from twitterscraper.tweet import Tweet

@generate_ordering('username', 'location', 'has_location', 'age', 'is_verified', 'total_tweets', 'total_following', 'total_followers', 'total_likes', 'total_moments', 'total_lists', 'has_avatar', 'has_background', 'is_protected', 'profile_modified', 'tweets')
class Profile:
    def __init__(self, username, location, has_location, age, is_verified, total_tweets, total_following, total_followers, total_likes, total_moments, total_lists, has_avatar, has_background, is_protected, profile_modified, tweets):
        self.username = username.replace("@", "")
        self.location = location
        self.has_location = has_location
        self.age = age
        self.is_verified = is_verified
        self.total_tweets = total_tweets
        self.total_following = total_following
        self.total_followers = total_followers
        self.total_likes = total_likes
        self.total_moments = total_moments
        self.total_lists = total_lists
        self.has_avatar = has_avatar
        self.has_background = has_background
        self.is_protected = is_protected
        self.profile_modified = profile_modified
        self.tweets = tweets


    @classmethod
    def from_soup(cls, soup):
        sideBar = soup.find('div', 'ProfileHeaderCard')
        topBar = soup.find('ul',  'ProfileNav-list')

        location=sideBar.find('div', 'ProfileHeaderCard-location').get_text().strip() or 0
        has_avatar=0 if 'default_profile_images' in soup.find('img', 'ProfileAvatar-image')['src'] else 1

        try:
            joined = sideBar.find('span', 'ProfileHeaderCard-joinDateText')['title']
            age = (datetime.now() - datetime.strptime(joined, "%I:%M %p - %d %b %Y")).days
        except:
            age = 0

        try:
            soup.find('div', 'ProfileCanopy-headerBg').find('img')['src']
            has_background = 1
        except:
            has_background = 0

        try:
            a = soup.find('h2', 'ProtectedTimeline-heading')
            protected = 1
        except:
            protected = 0
            
        try:
            total_moments=topBar.find('li', 'ProfileNav-item--moments').find('span', 'ProfileNav-value')['data-count'] or 0
        except:
            total_moments=0

        try:
            total_lists=topBar.find('li', 'ProfileNav-item--lists').find('span', 'ProfileNav-value')['data-count'] or 0
        except:
            total_lists=0

        tweets = soup.find_all('div', 'tweet')
        all_tweets = []

        for tweet in tweets:
            
            if " Retweeted" not in tweet.get_text():
                all_tweets.append(Tweet.from_soup(tweet))

        return cls(
            username=sideBar.find('span', 'username').text or "",
            location=location,
            has_location=0 if location == 0 else 1,
            age=age,
            is_verified=0 if sideBar.find('span', 'Icon--verified') == None else 1,
            total_tweets=topBar.find('li', 'ProfileNav-item--tweets').find('span', 'ProfileNav-value')['data-count'] or 0,
            total_following=topBar.find('li', 'ProfileNav-item--following').find('span', 'ProfileNav-value')['data-count'] or 0,
            total_followers=topBar.find('li', 'ProfileNav-item--followers').find('span', 'ProfileNav-value')['data-count'] or 0,
            total_likes=topBar.find('li', 'ProfileNav-item--favorites').find('span', 'ProfileNav-value')['data-count'] or 0,
            total_moments=total_moments,
            total_lists=total_lists,
            has_avatar=has_avatar,
            has_background=has_background,
            is_protected=protected,
            profile_modified=1 if has_background == 1 or has_avatar == 1 or location != 0 else 0,
            tweets=all_tweets
        )

    @classmethod
    def from_html(cls, html):
        soup = BeautifulSoup(html, "lxml")
        try:
            yield cls.from_soup(soup)
        except AttributeError:
            pass