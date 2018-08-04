import os
import logging

def myLogger(location):
    logger = logging.getLogger(location.split("/")[-1])
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(location, 'w')
    logger.addHandler(handler)
    return logger

logger = myLogger(os.getcwd() + "/a.log")
logger.info("abc")