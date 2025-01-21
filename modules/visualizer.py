
"""
Visualization Module
------------------
Generates visual representations of text data including word clouds,
frequency distributions, and readability metrics charts.

Author: Walter Ochieng
Email: ocu9@cdc.gov
Version: 1.0.0
Date: 2025-01-21
License: MIT

Visualization Types:
    - Word clouds
    - Frequency distribution plots
    - Readability score charts
    - Text complexity graphs
    - Token distribution visualizations

Dependencies:
    - matplotlib>=3.4.0
    - wordcloud>=1.8.0
    - PIL

Usage:
    from modules.visualization import Visualizer
    
    viz = Visualizer()
    wordcloud = viz.generate_wordcloud("Your text here")
    freq_plot = viz.plot_frequency_distribution(tokens)
"""
import matplotlib.pyplot as plt 
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import streamlit as st
import logging 
import numpy as np
from PIL import Image


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class Visualizer:
    @staticmethod
    @st.cache_data
    def plot_word_count_distribution(word_counts):
        """
        Plots a bar chart of word counts for each section of the manuscript.

        Args:
            word_counts (dict): A dictionary where keys are section names and values are the word counts of each section.

        Returns:
            None: The function displays the plot using Streamlit.
        """
        try:
            plt.figure(figsize=(10, 5))
            plt.bar(word_counts.keys(), word_counts.values())
            plt.title("Section Word Count Distribution")
            plt.xlabel("Section")
            plt.ylabel("Word Count")
            st.pyplot(plt)
        except Exception as e:
            logger.error(f"Error plotting word count distribution: {str(e)}")
            st.error("Failed to generate word count visualization.")

    @staticmethod
    @st.cache_data
    def generate_word_cloud(text, image_path=None):
        """
        Generates and displays a word cloud from the input text, with an optional image mask for shaping the cloud.

        Args:
            text (str): The full text to generate the word cloud from.
            image_path (str, optional): The path to an image file to shape the word cloud. If None, a simple word cloud is generated.

        Returns:
            None: The function displays the word cloud using Streamlit.
        """
        try:
            wordcloud = WordCloud(stopwords=STOPWORDS, background_color="white", width=800, height=400)

            if image_path:
                mask = np.array(Image.open(image_path))
                wordcloud = WordCloud(stopwords=STOPWORDS, background_color="white", mask=mask)
                image_colors = ImageColorGenerator(mask)
                wordcloud.generate(text)
                plt.figure(figsize=(10, 5))
                plt.imshow(wordcloud.recolor(color_func=image_colors), interpolation="bilinear")
            else:
                wordcloud.generate(text)
                plt.figure(figsize=(10, 5))
                plt.imshow(wordcloud, interpolation="bilinear")

            plt.axis("off")
            st.pyplot(plt)
        except Exception as e:
            logger.error(f"Error in generating word cloud: {str(e)}")
            st.error("Failed to generate word cloud visualization.")
