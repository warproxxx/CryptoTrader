from coala_utils.decorators import generate_ordering
import time

@generate_ordering('username', 'location', 'has_location', 'created', 'is_verified', 'total_tweets', 'total_following', 'total_followers', 'total_likes', 'has_avatar', 'has_background', 'is_protected', 'profile_modified')
class Profile:
    def __init__(self, username, location, has_location, created, is_verified, total_tweets, total_following, total_followers, total_likes, has_avatar, has_background, is_protected, profile_modified):
        self.username = username
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

    @classmethod
    def from_profile(cls, tweet):

        has_avatar = 0 if 'default_profile_images' in tweet.user.profile_image_url else 1
        has_background = int(tweet.user.profile_use_background_image)
        has_location = int(tweet.user.geo_enabled)
        if has_location == 1:
            location = tweet.user.location
        else:
            location = 0
            
        profile_modified = 1 if has_background == 1 or has_avatar == 1 or has_location != 0 else 0


        return cls(
            username=tweet.user.screen_name,
            location=location,
            has_location=has_location,
            created=tweet.user.created_at.strftime('%Y-%m-%d'),
            is_verified=int(tweet.user.verified),
            total_tweets=tweet.user.statuses_count,
            total_following=tweet.user.friends_count,
            total_followers=tweet.user.followers_count,
            total_likes=tweet.user.favourites_count,
            has_avatar=has_avatar,
            has_background=has_background,
            is_protected=int(tweet.user.protected),
            profile_modified=profile_modified
        )