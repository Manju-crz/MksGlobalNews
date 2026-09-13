"""
News scraping modules for MksGlobalNews
"""

from .finders.APNews import scrape_apnews
from .finders.BBC import scrape_bbc
from .finders.CBC import scrape_cbc
from .finders.DW import scrape_dw
from .finders.TheGuardian import scrape_guardian

from .pages.page_APNews import APNewsPage
from .pages.Page_BBC import BBCPage
from .pages.Page_CBC import CBCPage
from .pages.Page_DW import DWPage
from .pages.Page_TheGuardian import TheGuardianPage

from .utils.browser_utility import BrowserUtility
from .utils.common_utils import CommonUtils
from .utils.NewsScraper import NewsScraper

__all__ = [
    'scrape_apnews',
    'scrape_bbc',
    'scrape_cbc',
    'scrape_dw',
    'scrape_guardian',
    'APNewsPage',
    'BBCPage',
    'CBCPage',
    'DWPage',
    'TheGuardianPage',
    'BrowserUtility',
    'CommonUtils',
    'NewsScraper'
]
