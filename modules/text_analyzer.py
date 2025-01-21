
"""
Text Analysis Module
------------------
Provides comprehensive text analysis features including readability metrics,
syntax checking, and AI-powered content analysis.

Author: Walter Ochieng
Email: ocu9@cdc.gov
Version: 1.0.0
Date: 2025-01-21
License: MIT

Features:
    - Readability scoring (Flesch-Kincaid, SMOG, etc.)
    - Grammar and syntax checking
    - Sentiment analysis
    - Keyword extraction
    - Text statistics (word count, sentence length, etc.)

Dependencies:
    - nltk>=3.6.0
    - textstat
    - difflib

Usage:
    from modules.text_analysis import TextAnalyzer
    
    analyzer = TextAnalyzer()
    metrics = analyzer.analyze_text("Your input text here")
    readability = analyzer.get_readability_score("Your text here")
"""
from difflib import SequenceMatcher
import textstat
import streamlit as st
import os
from typing import Dict, List, Tuple, Union 
import logging
import re
import tiktoken
from modules.azure_client import AzureClient
from modules.file_handler import FileHandler

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
azure_client = AzureClient()
client = azure_client.setup_azure_client()
class TextAnalyzer:
    @staticmethod
    def count_tokens(text: str, model="gpt-3.5-turbo"):
        """
        Counts the number of tokens in the givn text using the specified AI model
        Parameters:
            text (str): The input text to be tokenized
            model (str): The model to use for selecting tokenizer
        Returns:
            int: The number of tokens in the text

        """
        try:
            tokenizer = tiktoken.encoding_for_model(model)
            tokens = tokenizer.encode(text)
            return len(tokens)
        except Exception as e:
            logger.error(f"An error occured when estimating number of tokens: {str(e)}")
            return None
        
    @staticmethod
    @st.cache_data(show_spinner=False)
    def extract_main_content(text: str) -> str:
        """
        Extract the main content of the text by removing references/citations section
        Args:
            text (str): The input text to process

        Returns:
            str: Text with the citations removed
        """
        reference_headers = [
                r"references?$",
                r"bibliography$",
                r"citations?$",
                r"works cited$",
                r"sources?$",
                r"references? cited$"
            ]
        pattern = r"(?i)^\s*(?:" + "|".join(reference_headers) + r")[\s:]*$"
        lines = text.split("\n")
        main_content = []
        in_references = False

        for i, line in enumerate(lines):
            if re.match(pattern, line.strip()):
                in_references = True
                break
            elif not in_references and i > 0:
                if re.match(r'^\s*(?:\[\d+\]|\d+\.|\(\d+\))\s+', line):
                    next_few_lines = lines[i:min(i+3, len(lines))]
                    if all(re.match(r'^\s*(?:\[\d+\]|\d+\.|\(\d+\))\s+', l) for l in next_few_lines):
                        in_references = True
                        break
            if not in_references:
                main_content.append(line)

        return '\n'.join(main_content)

    @staticmethod
    @st.cache_data(show_spinner=False)
    def readability_analysis(text: str) -> dict:
        main_content = TextAnalyzer.extract_main_content(text)
        try:
            readability_scores = {
                "Flesch Reading Ease": textstat.flesch_reading_ease(main_content),
                "SMOG Index": textstat.smog_index(main_content),
                "Gunning Fog Index": textstat.gunning_fog(main_content),
                "Automated Readability Index": textstat.automated_readability_index(main_content),
                "Coleman-Liau Index": textstat.coleman_liau_index(main_content),
                "Dale-Chall Readability Score": textstat.dale_chall_readability_score(main_content),
                "Linsear Write Formula": textstat.linsear_write_formula(main_content),
                "Difficult Words": textstat.difficult_words(main_content),
                "Text Standard": textstat.text_standard(main_content)
            }

            ranges = {
                "Flesch Reading Ease": {
                    "Easy": 60,
                    "Hard": 30
                },
                "SMOG Index": {
                    "Easy": 7,
                    "Hard": 12
                },
                "Gunning Fog Index": {
                    "Easy": 8,
                    "Hard": 12
                },
                "Automated Readability Index": {
                    "Easy": 8,
                    "Hard": 12
                },
                "Coleman-Liau Index": {
                    "Easy": 8,
                    "Hard": 12
                },
                "Dale-Chall Readability Score": {
                    "Easy": 5,
                    "Hard": 8
                },
                "Linsear Write Formula": {
                    "Easy": 10,
                    "Hard": 14
                }
            }

            descriptions = {
                "Flesch Reading Ease": {
                    "Easy": "Easily understood by a 13-15 year-old",
                    "Acceptable": "Suitable for academic writing",
                    "Hard": "Very difficult to read"
                }
            }

            annotated_scores = {}
            for metric, score in readability_scores.items():
                if metric in ranges:
                    if score > ranges[metric]["Easy"]:
                        difficulty = "Easy"
                    elif score < ranges[metric]["Hard"]:
                        difficulty = "Hard"
                    else:
                        difficulty = "Acceptable"
                    
                    desc = descriptions.get(metric, {}).get(difficulty, "")
                    annotated_scores[metric] = {
                        "Score": score, 
                        "Difficulty": difficulty,
                        "Description": desc
                    }
                else:
                    annotated_scores[metric] = {"Score": score}

            return annotated_scores
        except Exception as e:
            logger.error(f"Error in readability analysis: {str(e)}")
            return {"error": "Failed to analyze readability"}


       
    @staticmethod
    @st.cache_data(show_spinner=False)
    def highlight_differences(original, enhanced):
        try:
            matcher = SequenceMatcher(None, original, enhanced)
            result = []
            changes = []
            current_pos = 0
            for tag, i1, i2, j1, j2, in matcher.get_opcodes():
                if tag == "equal":
                    result.append(enhanced[j1:j2])
                elif tag == "replace":
                    result.append(f'<span style="background-color: #ffebee;">{enhanced[j1:j2]}</span>')
                    changes.append(["replace", j1, enhanced[j1:j2]])
                elif tag == "insert":
                    result.append(f'<span style="background-color:#e8f5e9;">{enhanced[j1:j2]}</span>')
                    changes.append(["insert", j1, enhanced[j1:j2]])
                elif tag == "delete":
                    result.append(f'<span style="background-color: #ffebee; text-decoration: line-through;">{original[i1:i2]}</span>')

            return "".join(result), changes
        except Exception as e:
            logger.error(f"Problems highlighting differences: {str(e)}")
            return enhanced, []
    
    @staticmethod
    @st.cache_data(show_spinner=False)
    def syntax_analysis(text):
        """
        Performs a basic syntax analysis on the given text, checking for common issues like 
        sentence length and punctuation balance.

        Args:
            text (str): The text to analyze.

        Returns:
            dict: A dictionary with syntax analysis results, such as average sentence length and
                whether the text has balanced punctuation.
        """
        main_content = TextAnalyzer.extract_main_content(text)
        # Split text into sentences
        sentences = main_content.split(". ")
        num_sentences = len(sentences)
        total_words = len(main_content.split())
        average_sentence_length = total_words / num_sentences if num_sentences > 0 else 0

        # Check for balanced punctuation (e.g., matching parentheses, quotes)
        punctuation_balance = {
            "Parentheses Balanced": main_content.count("(") == main_content.count(")"),
            "Quotes Balanced": main_content.count("\"") % 2 == 0
        }

        syntax_results = {
            "Average Sentence Length": average_sentence_length,
            "Punctuation Balance": punctuation_balance
        }
        return syntax_results
    
    @staticmethod
    @st.cache_data(show_spinner=False)
    def generate_elevator_pitch(_client, text, summary_length="short"):
        """
        Make summaries of document. Three options: short, medium, and detailed
        """
        main_content = TextAnalyzer.extract_main_content(text)
        if not client:
            return "AI Summarization currently unavailable. Please try later!"
        summary_config = {
                "short": {
                        "prompt":  "You are an epidemiologist. Create a high-level summary in 50 words or less based on this text.",
                        "max_tokens": 50,
                    },
                "medium": {
                        "prompt":  "You are an epidemiologist. Create a high-level summary in 100 words or less based on this text.",
                        "max_tokens": 150,
                    },
                "detailed": {
                        "prompt":  "You are an epidemiologist. Create a high-level summary in 150 words or less based on this text.",
                        "max_tokens": 250,
                    }
            }
        config = summary_config.get(summary_length.lower(), summary_config["short"])
        try:
            response = client.chat.completions.create(
                    model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
                    messages=[
        
                        {"role": "system", "content": config["prompt"]},
                        {"role": "user", "content": main_content}
                    ],
                    temperature=0.7,
                    max_tokens=config["max_tokens"]
                )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Failed in generating document summary. {str(e)}")
            return "Failed to generate document summary. Please try again later."
        
    @staticmethod
    @st.cache_data(show_spinner=False)
    def analyze_text_ai(_client, text, max_words = None):
        """Analyze text using Azure OpenAI with error handling and word limits to conserve computing resources"""
        if not client:
            return "AI analysis is currently unavailable. Please try again later."

        main_content = TextAnalyzer.extract_main_content(text)
        try:
            max_tokens = int(max_words * 1.3) if max_words else 3000
            response = client.chat.completions.create(
                model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
                messages=[
                    {"role": "system", "content": "You are a professional epidemiological journal editor. Analyze the following text and suggest improvements."},
                    {"role": "user", "content": main_content}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return "Failed to get AI suggestions. Please try again later."
