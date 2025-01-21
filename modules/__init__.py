
"""
Modules Package Initialization
---------------------------
Initializes the modules package for the Streamlit Document Editor,
exposing key classes and functions to the main application.

Author: Walter Ochieng
Email: ocu9@cdc.gov
Version: 1.0.0
Date: 2025-01-21
License: MIT

Exposed Components:
    - AzureClient
    - FileHandler
    - TextAnalyzer
    - Visualizer
    - utility functions

Usage:
    from modules import AzureClient, FileHandler, TextAnalyzer, Visualizer
"""
from .utils import Utils
from .visualizer import Visualizer
from .azure_client import AzureClient
from .file_handler import FileHandler
from .text_analyzer import TextAnalyzer

__all__ = ['Utils', 'Visualizer', 'AzureClient', 'FileHandler', 'TextAnalyzer']
