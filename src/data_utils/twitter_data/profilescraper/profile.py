from datetime import datetime
from bs4 import BeautifulSoup

from coala_utils.decorators import generate_ordering
from twitterscraper.tweet import Tweet

@generate_ordering('username', 'location', 'has_location', 'created', 'is_verified', 'total_tweets', 'total_following', 'total_followers', 'total_likes', 'has_avatar', 'has_background', 'is_protected', 'profile_modified', 'tweets')
class Profile:
    def __init__(self, username, location, has_location, created, is_verified, total_tweets, total_following, total_followers, total_likes, has_avatar, has_background, is_protected, profile_modified, tweets):
        self.username = username.replace("@", "")
        self.location = location
        self.has_location = has_location
        self.created = created
        self.is_verified = is_verified
        self.total_tweets = total_tweets
        self.total_following = total_following
        self.total_followers = total_followers
        self.total_likes = total_likes
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
            created = datetime.strptime(joined, "%I:%M %p - %d %b %Y").strftime("%Y-%m-%d")
           
        except Exception as e:
            print(str(e))
            created = 0

        try:
            soup.find('div', 'ProfileCanopy-headerBg').find('img')['src']
            has_background = 1
        except:
            has_background = 0

        try:
            a = soup.find('h2', 'ProtectedTimeline-heading')

            if a == None:
                protected = 0
            else:
                protected = 1
        except:
            protected = 0
            
        tweets = soup.find_all('div', 'tweet')
        all_tweets = []

        for tweet in tweets:
            
            if " Retweeted" not in tweet.get_text():
                all_tweets.append(Tweet.from_soup(tweet))

        return cls(
            username=sideBar.find('span', 'username').text or "",
            location=location,
            has_location=0 if location == 0 else 1,
            created=created,
            is_verified=0 if sideBar.find('span', 'Icon--verified') == None else 1,
            total_tweets=topBar.find('li', 'ProfileNav-item--tweets').find('span', 'ProfileNav-value')['data-count'] or 0,
            total_following=topBar.find('li', 'ProfileNav-item--following').find('span', 'ProfileNav-value')['data-count'] or 0,
            total_followers=topBar.find('li', 'ProfileNav-item--followers').find('span', 'ProfileNav-value')['data-count'] or 0,
            total_likes=topBar.find('li', 'ProfileNav-item--favorites').find('span', 'ProfileNav-value')['data-count'] or 0,
            has_avatar=has_avatar,
            has_background=has_background,
            is_protected=protected,
            profile_modified=1 if has_background == 1 or has_avatar == 1 or location != 0 else 0,
            tweets=all_tweets
        )

    @classmethod
    def from_html(cls, html):
        soup = BeautifulSoup(html, "lxml")
        profile = Profile.from_soup(soup)
        return profile