import threading
import time

from livescraper.query import query_tweets

keywords = {}
qt = query_tweets(keywords)
logger, keywordsOnly, listener, myStream = qt.get_stream()
                
while True:
    try:
        myStream.filter(track=keywordsOnly, languages=['en'])
    except KeyboardInterrupt:
        df, userData, start_time = listener.get_data()     
        logger.info("Keyboard interrupted. Saving whatever has been collected")
        
        t1 = threading.Thread(target=qt.save_data, args=[df, userData, start_time, int(time.time())])
        t1.start()

    except Exception as e:
        logger.warning(('Got an exception. Error is: {}. Saving whatever exists').format(str(e)))
        df, userData, start_time = listener.get_data()                                
        
        end_time = int(time.time())
        
        t1 = threading.Thread(target=qt.save_data, args=[df, userData, start_time, end_time])
        t1.start()                

        logger, _, listener, myStream = qt.get_stream()