# import os
# from glob import glob
# from libs.writing_utils import get_locations, get_logger
# from libs.reading_utils import get_keywords

# from utils.scrape import scrapeUtils
# from utils.scrape import historicDownloader

# import datetime

# class TestscrapeUtils:

#     def setup_method(self):
#         liveKeywords, self.keywords = get_keywords("/tests/keywords.json")
#         _, self.currRoot_dir = get_locations()
#         self.relativedir = "/utils/tests/"
#         self.su = scrapeUtils(self.keywords)

#     def test_move_live_data(self):
#         self.su.move_live_data(self.relativedir)

# class TesthistoricDownloader:

#     def setup_method(self):
#         liveKeywords, self.detailsList = get_keywords("/tests/keywords.json")
#         _, self.currRoot_dir = get_locations()

#         logger = get_logger(self.currRoot_dir + '/utils/tests/logs/historic_logs.txt')

#         self.hd = historicDownloader(self.detailsList, logger=logger, relative_dir="/utils/tests/")

#     def test_scrape(self):
#         pass
#         # data = self.hd.scrape(datetime.datetime(2018,6,2, 0, 0, 0), datetime.datetime(2018, 6, 3, 23, 59, 59), form="save", proxy=None, keyword='Bitcoin OR BTC', coinname='Bitcoin')
#         # print(data)
        
#     def test_perform_scraping(self):
#         pass
