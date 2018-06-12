from datetime import datetime
from bs4 import BeautifulSoup

from coala_utils.decorators import generate_ordering

@generate_ordering('username')
class Profile:
    def __init__(self):
        pass