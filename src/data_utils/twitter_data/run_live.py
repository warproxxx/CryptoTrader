import threading
import time

from livescraper.query import query_tweets, get_listener, save_data

keywords = {}
logger, keywordsOnly, listener, myStream = query_tweets(keywords)
                
while True:
    try:
        myStream.filter(track=keywordsOnly, languages=['en'])
    except KeyboardInterrupt:
        df, userData, start_time = listener.get_data()     
        logger.info("Keyboard interrupted. Saving whatever has been collected")
        
        t1 = threading.Thread(target=save_data, args=[df, userData, start_time, int(time.time()), coins])
        t1.start()

    except Exception as e:
        logger.warning(('Got an exception. Error is: {}. Saving whatever exists').format(str(e)))
        df, userData, start_time = listener.get_data()                                
        
        end_time = int(time.time())
        
        t1 = threading.Thread(target=save_data, args=[df, userData, start_time, end_time, coins])
        t1.start()                
        
        listener, auth = get_listener(keywords)
        myStream = Stream(auth=auth, listener=listener)