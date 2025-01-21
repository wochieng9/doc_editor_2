# Streamlit Document Editor

A powerful document editing and analysis application built with Streamlit, featuring text analysis, visualization, and Azure integration.

## Features

- Document editing with real-time preview
- Advanced text analysis including readability metrics and syntax checking
- Word cloud visualization
- Azure integration for cloud storage
- File import/export capabilities
- NLTK-based text processing

## Project Structure

```
project/
├── app.py                  # Main Streamlit app entry point
├── modules/
│   ├── __init__.py        # Initializes the `modules` package
│   ├── azure_client.py    # Azure client setup and interactions
│   ├── file_handling.py   # File reading and saving logic
│   ├── text_analysis.py   # Readability, syntax, and AI-based analysis
│   ├── visualization.py   # Word cloud and plotting functions
│   ├── utils.py          # Utility functions (e.g., logging, NLTK setup)
├── requirements.txt       # Python dependencies
└── .env                  # Environment variables
```

## Installation

1. Clone the repository:
```bash
git # Will add path
cd streamlit-document-editor
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your Azure credentials:
```
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
AZURE_CONTAINER_NAME=your_container_name
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to `http://localhost:8501`

3. Use the sidebar controls to:
   - Upload documents
   - Edit text
   - Generate visualizations
   - Analyze text metrics
   - Save to Azure cloud storage

## Module Descriptions

### azure_client.py
Handles all Azure Storage interactions, including file upload, download, and listing operations.

### file_handling.py
Manages local file operations, including reading various file formats and saving edited documents.

### text_analysis.py
Provides text analysis features such as:
- Readability scoring
- Grammar checking
- Sentiment analysis
- Keyword extraction

### visualization.py
Creates visual representations of document data, including:
- Word clouds
- Frequency distributions
- Readability metrics charts

### utils.py
Contains utility functions for:
- NLTK setup and management
- Logging configuration
- Common helper functions

## Dependencies

Key dependencies include:
- streamlit
- azure-storage-blob
- nltk
- pandas
- matplotlib
- wordcloud
- python-dotenv

See `requirements.txt` for a complete list of dependencies.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Acknowledgments

- Streamlit team for the amazing framework
- NLTK project for natural language processing tools
- Azure team for cloud storage solutions


