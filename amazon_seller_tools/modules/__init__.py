"""
亚马逊卖家智能辅助系统 - 核心模块
"""

from .product_research import ProductResearch
from .operations import OperationsManager
from .inventory import InventoryManager
from .advertising import AdvertisingOptimizer
from .ranking import RankingAnalyzer
from .competitor import CompetitorAnalyzer
from .listing import ListingOptimizer

__all__ = [
    'ProductResearch',
    'OperationsManager',
    'InventoryManager',
    'AdvertisingOptimizer',
    'RankingAnalyzer',
    'CompetitorAnalyzer',
    'ListingOptimizer'
]

__version__ = '1.0.0'
