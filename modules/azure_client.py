"""
Azure Storage Client Module
--------------------------
Handles Azure Blob Storage operations for the Streamlit Document Editor,
providing cloud storage functionality for documents and user data.

Author: Walter Ochieng
Email: ocu9@cdc.gov
Version: 1.0.0
Date: 2025-01-21
License: MIT

Environment Variables Required:
    - AZURE_STORAGE_CONNECTION_STRING: Azure storage connection string
    - AZURE_CONTAINER_NAME: Target container name

Dependencies:
    - openai
    - python-dotenv>=0.19.0

Usage:
    from modules.azure_client import AzureClient
    
    client = AzureClient()
"""
import os
from azure.identity import ClientSecretCredential
from openai import AzureOpenAI
from dotenv import load_dotenv
import logging


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
class AzureClient:
    def setup_azure_client(self):
        """Set up and return Azure OpenAI client"""
        try:
            load_dotenv()
            credential = ClientSecretCredential(
                tenant_id=os.environ.get("SP_TENANT_ID"),
                client_id=os.environ.get("SP_CLIENT_ID"),
                client_secret=os.environ.get("SP_CLIENT_SECRET")
            )
            token = credential.get_token("https://cognitiveservices.azure.com/.default").token

            # Set required environment variables
            os.environ["OPENAI_API_VERSION"] = "2023-05-15"
            os.environ["OPENAI_API_TYPE"] = "azure_ad"
            os.environ["AZURE_OPENAI_API_KEY"] = token
            
            return AzureOpenAI(
                api_key=token,
                azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
                api_version="2023-05-15"
            )
        except Exception as e:
            logger.error(f"Failed to setup Azure client: {str(e)}")
            return None
