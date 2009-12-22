from django.conf import settings

try:
    import twitter
except ImportError:
    twitter = None


def can_tweet():
    creds_available = (hasattr(settings, "TWITTER_USERNAME") and
                       hasattr(settings, "TWITTER_PASSWORD"))
    return twitter and creds_available