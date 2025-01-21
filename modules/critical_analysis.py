
"""
Modules Package Initialization
---------------------------
Provides text analysis, editing and generate summaries for the document analyzer.
Also assess methodology if appropriate.

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
    from modules import AzureClient,os, logging
"""
import streamlit as st
from modules.azure_client import AzureClient
import logging
import os

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class CriticalAnalyzer:
    def __init__(self):
        """Initialize the CriticalAnalyzer with Azure client"""
        self.azure_client = AzureClient()
        self.client = self.azure_client.setup_azure_client()

    def get_completion(self, messages, temperature=0.7, max_tokens=3000):
        """Get completion from Azure OpenAI"""
        if not self.client:
            raise ValueError("Azure OpenAI client not initialized")
        try:
            response = self.client.chat.completions.create(
                model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-35-turbo"),
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error in getting completion: {str(e)}")
            raise

    def extract_research_question(self, text: str, temperature: float = 0.7, max_tokens: int = 100) -> str:
        """Extract research question from text using Azure OpenAI"""
        try:
            prompt = f"""
            You are a PhD-level researcher in epidemiology. Extract the main research question from the following text.
            If there is no explicit question, please infer the most likely research question based on the content.
            Text: {text}
            """
            messages = [
                {"role": "system", "content": "You are a PhD level science research expert."},
                {"role": "user", "content": prompt},
            ]
            return self.get_completion(messages, temperature=temperature, max_tokens=max_tokens)
        except Exception as e:
            logger.error(f"Error in extracting research question: {str(e)}")
            return "Failed to extract research question."

    def critical_review(self, text: str, research_question: str,
                       temperature: float = 0.7, max_tokens: int = 500) -> str:
        """Perform critical review of methodology"""
        try:
            prompt = f"""
            You are a PhD-level statistician or econometrician. Critically evaluate the methodology of
            the following paper {text} in the context of the research question {research_question}.
            The content might fall under an explicitly described methods section or be randomly placed in the text.
            Provide a detailed review that includes:
            - The appropriateness of the method to answer the research question
            - Any limitations or potential biases of the methods used
            - Suggestions for improving methodology
            - Recommendations for alternative approaches if applicable
            """
            messages = [
                {"role": "system", "content": "You are a PhD statistician/econometrician."},
                {"role": "user", "content": prompt},
            ]
            return self.get_completion(messages, temperature=temperature, max_tokens=max_tokens)
        except Exception as e:
            logger.error(f"Error in critical review generation: {str(e)}")
            return "Failed to conduct critical review. Recheck manuscript length and paste methods only."


    def analyze_methods(self, text: str) -> dict:
        """Complete method analysis including research question extraction and review"""
        try:
            logger.info("Trying to extract research question")
            research_question = self.extract_research_question(text)
            logger.info("Extracted research question")
            
            if not research_question or research_question.lower() == "no research question found":
                return {
                    "research_question": "Could not extract research question.",
                    "review": "Cannot perform a critical review without a valid research question."
                }
                
            review = self.critical_review(text, research_question)
            return {
                "research_question": research_question,
                "review": review
            }
        except Exception as e:
            logger.error(f"Error in analyzing methods: {str(e)}")
            return {
                "research_question": "Error occurred while extracting research question.",
                "review": "Error occurred while analyzing methods."
            }

    @staticmethod
    @st.cache_data
    def _cached_analyze_title(_client, title:str, text:str, temperature: float=.7, max_tokens: int=100)-> str:
        """Cached version of title analysis"""
        try:
            prompt = f"""
                    You are a scientific journal editor. Analyze the following title in relation to the paper's content:
                    Title: {title}
                    Paper content: {text}
                    Please evaluate:
                    1. Clarity and conciseness
                    2. Accuracy in reflecting the paper's content
                    3. Use of appropriate keywords
                    4. SEO-friendliness
                    5. Adherence to scientific paper title conventions
                    6. Relevant time period if warranted
                    7. Whether it accurately communicates the main findings/methodology

                    Provide specific recommendations for improvement if needed.
        
            """
            messages = [
                    {"role": "system", "content": "You are an experienced scientific journal editor."},
                    {"role": "user", "content": prompt}
                ]

            response = client.chat.completions.create(
                    model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-3.5-turbo"),
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error in analyzing title: {str(e)}")
            return "Failed to analyze the title"

    def analyze_title(self, title: str, text:str, temperature: float = 0.7) -> str:
        """Analyze the appropriateness of the paper title"""
        return self._cached_analyze_title(self.client, title, text, temperature)






























    
