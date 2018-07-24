from libs.filename_utils import get_locations, get_name
import os

def test_get_name():
    name = get_name()
    assert("test_filename_utils" in name)
    assert(os.getcwd() in name)
    assert(__file__ in name)
    

def test_get_locations():
    name, rootDir = get_locations("twitter_data")
    print(rootDir.split("twitter_data")[0] in __file__)