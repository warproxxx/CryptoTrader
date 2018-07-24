from libs.reading_utils import proxy_dict, get_proxies, get_twitter
import os

def test_proxy_dict():
    returnedDic = proxy_dict("1.2.2.3")
    assert (len(returnedDic.keys()) == 3)
    assert (returnedDic['http'] == "http://1.2.2.3")
    assert (returnedDic['https'] == "https://1.2.2.3")
    assert (returnedDic['ftp'] == "ftp://1.2.2.3")

def test_get_proxies():
    proxies = get_proxies()
    assert(len(proxies) > 1)

    location = "/" + os.path.realpath(__file__).split("twitter_data/")[1].replace(__file__.split("/")[-1], "") + "proxies.txt"
    
    proxies = get_proxies(location)
    assert(len(proxies) == 3)
    assert(proxies[0]['http'] == "http://1.1.1.1")
    assert(proxies[1]['https'] == "https://2.2.2.2")
    assert(proxies[2]['ftp'] == "ftp://3.3.3.3")

def test_get_twitter():
    twitter = get_twitter()

    assert(len(twitter) == 4)

    location = "/" + os.path.realpath(__file__).split("twitter_data/")[1].replace(__file__.split("/")[-1], "") + "api.json"
    twitter = get_twitter(location)

    assert(twitter[0] == "95fyXonGGIHKgfothfbOOAM7p")
    assert(twitter[1] == "6KWDuC87go4CbFE6jLdRnHWGFcj2Fl9hQvdizfaiwCOdZliv49")
    assert(twitter[2] == "852009551876431872-OfvYX17eqrPz9eERGaRVxKfkBPVALyO")
    assert(twitter[3] == "koQa3hgW22EsgdvseQVsj3KnYbzHc564xEVfr7lYiPGhy")