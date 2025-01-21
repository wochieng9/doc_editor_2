"""
Utilities Module
--------------
Provides utility functions and helper methods for the Streamlit Document Editor,
including logging configuration and NLTK resource management.

Author: Walter Ochieng
Email: ocu9@cdc.gov
Version: 1.0.0
Date: 2025-01-21
License: MIT

Functions:
    - Logging setup and configuration
    - NLTK resource downloading and management
    - Common text processing utilities
    - Error handling and validation
    - Configuration management

Dependencies:
    - nltk>=3.6.0
    - python-dotenv>=0.19.0
    - logging>=0.5.1.2

Usage:
    from modules.utils import setup_logging, download_nltk_resources
    
    logger = setup_logging()
    download_nltk_resources()
"""
import nltk
import logging
import streamlit as st

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class Utils:
    @staticmethod
    @st.cache_resource
    def download_nltk_data():
        """Downloads requires the NLTK library """
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            try:
                nltk.download('punkt')
                nltk.download('stopwords')
            except Exception as e:
                logger.error(f"Failed to download NLTK data: {str(e)}")
                st.warning("Some text analysis features may be limited due to resource download issues.")

