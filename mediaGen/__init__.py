"""
Media generation tools for MksGlobalNews
"""

from .audioGenerator import AudioGenerator
from .picsGenerator import generate_image_for_article

__all__ = [
    'AudioGenerator',
    'generate_image_for_article'
]
