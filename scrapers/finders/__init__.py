"""
News finder modules for discovering news articles from various sources
"""

from .APNews import scrape_apnews
from .BBC import scrape_bbc
from .CBC import scrape_cbc
from .DW import scrape_dw
from .TheGuardian import scrape_guardian

__all__ = [
    'scrape_apnews',
    'scrape_bbc',
    'scrape_cbc',
    'scrape_dw',
    'scrape_guardian'
]
