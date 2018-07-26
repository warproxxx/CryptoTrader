from libs.run_utils import runUtils
import os
from libs.filename_utils import get_locations

class TestrunUtils():

    def setup_method(self):
        self.keywords = {'bitcoin': ['bitcoin', 'BTC'], 'dashcoin': ['dashcoin', 'DASH', 'darkcoin']}
        self.ru = runUtils(self.keywords)
        _, self.currRoot_dir = get_locations()  

    def test_create_remove_directory_structure(self):
        self.ru.create_directory_structure()

        assert(os.path.isdir(self.currRoot_dir + "/data/profile/storage/raw"))
        assert(os.path.isdir(self.currRoot_dir + "/data/profile/storage/interpreted"))
        assert(os.path.isdir(self.currRoot_dir + "/data/profile/live"))

        for coinname, _ in self.keywords.items():
            assert(os.path.isdir(self.currRoot_dir + "/data/tweet/{}/live".format(coinname)))
            assert(os.path.isdir(self.currRoot_dir + "/data/tweet/{}/historic_scrape/raw".format(coinname)))
            assert(os.path.isdir(self.currRoot_dir + "/data/tweet/{}/historic_scrape/interpreted".format(coinname)))
            
            assert(os.path.isdir(self.currRoot_dir + "/data/tweet/{}/live_storage/interpreted/top_raw".format(coinname)))
            assert(os.path.isdir(self.currRoot_dir + "/data/tweet/{}/live_storage/interpreted/features".format(coinname)))
            assert(os.path.isdir(self.currRoot_dir + "/data/tweet/{}/live_storage/interpreted/network".format(coinname)))
            assert(os.path.isdir(self.currRoot_dir + "/data/tweet/{}/live_storage/archive".format(coinname)))


        self.ru.remove_directory_structure()

        for coinname, _ in self.keywords.items():
            assert(not(os.path.isdir(self.currRoot_dir + "/data/tweet/{}")))