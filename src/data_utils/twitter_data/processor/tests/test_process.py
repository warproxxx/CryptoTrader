from processor import historicProcessor
from libs.reading_utils import get_keywords
from libs.writing_utils import get_locations

import pandas as pd

class TesthistoricProcessor:
    
    def setup_method(self):
        _, historicList = get_keywords()
        historicList = [historicList[0]]
        self.hp = historicProcessor(historicList, relative_dir="twitterscraper/tests")
        _, self.curr_Root = get_locations()

    def test_read_merge(self):
        self.hp.read_merge(delete=False)

        df = pd.read_csv("{}/twitterscraper/tests/data/tweet/bitcoin/historic_scrape/raw/combined.csv".format(self.curr_Root), lineterminator='\n')
        assert(df.shape[0] == 20405)
        assert(df.shape[1] == 9)

    def test_create_ml_features(self):
        self.hp.create_ml_features()

        df = pd.read_csv("{}/twitterscraper/tests/data/tweet/bitcoin/historic_scrape/raw/combined.csv".format(self.curr_Root))
        
