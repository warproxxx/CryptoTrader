from libs.writing_utils import get_locations, get_name, get_logger
import os

def test_get_name():
    name = get_name()
    assert("test_writing_utils" in name)
    assert(os.getcwd() in name)
    assert(__file__ in name)
    

def test_get_locations():
    name, rootDir = get_locations("twitter_data")
    assert(rootDir.split("twitter_data")[0] in __file__)

def test_get_logger():
    name, rootDir = get_locations()
    flocation = rootDir + "/libs/tests/test.log"
    logger = get_logger(flocation)
    logger.info("abc")

    assert(os.path.exists(flocation))

    with open(flocation, 'r') as f:
        assert(f.readlines()[0] == 'abc\n')

    os.remove(flocation)
    
    assert(not(os.path.exists(flocation)))