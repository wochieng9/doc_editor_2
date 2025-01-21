

"""
Streamlit Document Editor
------------------------
Main application entry point for the Streamlit Document Editor, a web-based tool
for document editing and analysis with real-time text metrics and visualizations.

This module initializes the Streamlit interface and coordinates all core functionalities
including file handling, text analysis, and cloud storage integration.

Author: Walter Ochieng
Email: ocu9@cdc.gov
Version: 1.0.0
Date: 2025-01-21
License: MIT

Project Repository: TBD
Environment Variables Required:
    - AZURE_STORAGE_CONNECTION_STRING: Azure storage account connection string
    - AZURE_CONTAINER_NAME: Azure container name for document storage

Dependencies:
    - streamlit>=1.28.0
    - pandas>=2.0.0
    - azure-storage-blob>=12.0.0
    - nltk>=3.6.0

Usage:
    To run the application:
        $ streamlit run app.py

    The application will be available at http://localhost:8501 -- Thomas to decide
"""

import streamlit as st
from modules.azure_client import AzureClient
from modules.file_handler import FileHandler
from modules.text_analyzer import TextAnalyzer
from modules.visualizer import Visualizer
from modules.utils import Utils
from modules.critical_analysis import CriticalAnalyzer
import pyperclip
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import logging 
import matplotlib.pyplot as plt 
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    st.set_page_config(layout="wide", page_title="Scientific Manuscript Editor")
    st.markdown("""
    <style>
    .stMarkdown span {
                background-color: #ffebee;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'disclaimer_accepted' not in st.session_state:
        st.session_state.disclaimer_accepted = False
    if 'uploaded_text' not in st.session_state:
        st.session_state.uploaded_text = ""

    st.title("Scientific Manuscript Editor")

    # Disclaimer handling
    if not st.session_state.disclaimer_accepted:
        st.markdown("""
        ### Disclaimer
        Please read and accept the following disclaimer before proceeding:
        
        1. This tool is designed to assist in manuscript editing and analysis but should not be relied upon as the sole source of editing.
        2. The accuracy of analysis depends on the quality of the input text.
        3. Always review suggestions manually before implementing them.
        4. This tool does not guarantee publication readiness or academic acceptance.
        5. Your document remains your intellectual property and is not stored or shared.
        """)
        
        if st.checkbox("I have read and accept the disclaimer"):
            st.session_state.disclaimer_accepted = True
            st.rerun()

    elif st.session_state.disclaimer_accepted:
        # File upload
        st.header("Upload Your Document")
        upload_col1, upload_col2 = st.columns([2, 1])
        utils = Utils()
        utils.download_nltk_data()

        azure_client = AzureClient()
        client = azure_client.setup_azure_client()

        file_handler = FileHandler()
        text_analyzer = TextAnalyzer()
        visualizer = Visualizer()
        analyzer = CriticalAnalyzer()
        

        with upload_col1:
            uploaded_file = st.file_uploader(
                "Choose a file", 
                type=['txt', 'docx', 'pdf'],
                help="Supported formats: TXT, DOCX, PDF"
            )

        # Process uploaded file
        if uploaded_file:
            try:
                text = file_handler.read_file(uploaded_file)
                st.session_state.uploaded_text = text
                st.success(f"Successfully loaded {uploaded_file.name}")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")


        # Main editor
        st.header("Document Editor")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Text")
            text = st.text_area(
                "Edit your text here",
                value=st.session_state.uploaded_text,
                height=400,
                key="original_text"
            )
            
            if text:
                words = word_tokenize(text)
                sentences = sent_tokenize(text)
                
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                with metric_col1: st.metric("Words", len(words))
                with metric_col2: st.metric("Characters", len(text))
                with metric_col3: st.metric("Sentences", len(sentences))

        with col2:
            st.subheader("Enhanced Text")
            if text:
                analysis_type = st.selectbox(
                    "Enhancement Type",
                    ["AI Editor", "Manual Edit", "Format Only"]
                )
                if analysis_type == "AI Editor":
                    if "regenerate_counter" not in st.session_state:
                        st.session_state.regenerate_counter = 0
                    words = text.split()
                    numwords = len(words)
                    if numwords > 3000:
                        st.error(f"Text is too long ({numwords} words). Maximum allowed is 3000 words. Please reduce the text length and try again. Can delete references.")
                        st.stop()
                    max_words = st.sidebar.slider(
                        "Maximum desired word length",
                        min_value = 100,
                        max_value = 3000,
                        value = numwords,
                        step = 50,
                        help = "Limit the length of text to <3000 for analysis"
                    )
                    with st.spinner("Analyzing with Azure AI...."):
                        enhanced_text = text_analyzer.analyze_text_ai(client, text + f"_{st.session_state.regenerate_counter}", max_words=numwords)
                        highlighted_text, changes = text_analyzer.highlight_differences(text, enhanced_text)
                        st.markdown(highlighted_text, unsafe_allow_html=True)
                        if st.sidebar.button("Regenerate analysis"):
                            st.session_state.regenerate_counter +=1
                            st.rerun()


                        
                elif analysis_type == "Manual Edit":
                    enhanced_text = st.text_area(
                        "Edit Manually",
                        value=text,
                        height=400
                    )
                    highlighted_text, changes = text_analyzer.highlight_differences(text, enhanced_text)
                    st.markdown(highlighted_text, unsafe_allow_html=True)
                else:
                    enhanced_text = text
                    highlighted_text, changes = text, None
                    
                with st.expander("Changes Summary"):
                    added = len(enhanced_text) - len(text)
                    st.metric("Length change", added, f"{added:+d} characters")

                    if analysis_type != "Format Only":
                        import difflib
                        d = difflib.Differ()
                        diff = list(d.compare(text.splitlines(), enhanced_text.splitlines()))
                        st.code("\n".join(diff), language="diff")


                format_type = st.selectbox("Export Format", ['txt', 'docx', 'pdf'])
                # Prepare download content
                if format_type == 'txt':
                    download_content = enhanced_text
                    mime_type = 'text/plain'
                else:
                    print("Changes before save")
                    
                    download_content = file_handler.save_edited_document(enhanced_text, format_type, changes)
                    mime_type = f'application/{format_type}'
                
                if st.download_button(
                    label="Download Enhanced Version",
                    data=download_content,
                    file_name=f"enhanced_text.{format_type}",
                    mime=mime_type
                ):
                    
                    st.success("Document downloaded successfully!")      

        # Sidebar analysis tools
        st.sidebar.title("Analysis Tools")
               
            
        if text and st.sidebar.checkbox("Readability Analysis"):
            st.sidebar.subheader("Readability Analysis")
            results = text_analyzer.readability_analysis(text)
            for metric, data in results.items():
                if isinstance(data, dict) and "Score" in data:
                    score = data["Score"]
                    if isinstance(score, (int, float)):
                        score = round(score, 2)
                    difficulty = data.get("Difficulty", "")
                    
                    # Create colored metric display
                    color = {
                         "Easy": "green",
                         "Acceptable": "orange",
                         "Hard": "red"
                    }.get(difficulty, "black")
                     
                    st.sidebar.markdown(f"**{metric}**: {score} ")
                    if difficulty:
                        st.sidebar.markdown(f"*Difficulty*: :{color}[{difficulty}]")
                        st.sidebar.divider()

        summary_length = st.sidebar.selectbox(
                "Select Summary Length",
                ["Short", "Medium", "Detailed"],
            )

        if text and st.sidebar.checkbox("Generate Summary"):
                with st.spinner(f"Generating {summary_length.lower()} summary ...."):
                    summary = text_analyzer.generate_elevator_pitch(client, text, summary_length = summary_length.lower())
                    st.sidebar.subheader("Summary")
                    st.sidebar.write(summary)
                    word_count = len(summary.split())
                    st.sidebar.caption(f"Word count: {word_count}")
                    if st.button("Copy to clipboard"):
                        try:
                            pyperclip.copy(summary)
                            st.write("Summary copied to clipboard!")
                        except Exception as e:
                            logger.error(f"Error copying document summary to clipboard: {str(e)}")
                            st.error("Failed to copy. Please select and copy manually.")
        if text and st.sidebar.checkbox("Critical Analysis"):
            st.sidebar.subheader("Methodology Analysis")

            if "review_copied" not in st.session_state:
                st.session_state.review_copied = False
            if "question_copied" not in st.session_state:
                st.session_state.question_copied = False
                
            def copy_question():
                try:
                    pyperclip.copy(st.session_state.research_question)
                    st.session_state.question_copied = True
                except Exception as e:
                    logger.error(f"Error copying research question: {str(e)}")
                    st.session_state.question_copied = False

            def copy_review():
                try:
                    pyperclip.copy(st.session_state.review_text)
                    st.session_state.review_copied = True
                except Exception as e:
                    logger.error(f"Error copying critical review text: {str(e)}")
                    st.session_state.review_copied = False
                    
            temperature = st.sidebar.slider(
                "Analysis Temperature",
                min_value = 0.0,
                max_value = 1.0,
                value = 0.7,
                help = "Lower temperatures make the analysis deterministic"
            )      
            if st.sidebar.button("Analyze Methodology"):
                with st.spinner("Analyzing methodology....."):
                    try:
                        analysis_results = analyzer.analyze_methods(text)
                        st.sidebar.markdown("***Research Question***")
                        st.session_state.research_question = analysis_results["research_question"]
                        st.sidebar.info(st.session_state.research_question)

                        st.sidebar.markdown("***Critical review***")
                        st.session_state.review_text = analysis_results["review"]
                        st.sidebar.write(st.session_state.review_text)
                        
                        col1, col2 = st.sidebar.columns(2)
                        with col1:
                            if st.button("Copy question", on_click = copy_question):
                                pass
                            if st.session_state.question_copied:
                                st.success("Research question copied!")

                        with col2:
                            if st.button("Copy review", on_click = copy_review):
                                pass
                            if st.session_state.review_copied:
                                st.success("Review copied!")
                                
                    except Exception as e:
                        st.sidebar.error(f"Error in critical analysis: {str(e)}")
                        logger.error(f"Critical analysis error: {str(e)}")

        if text and st.sidebar.checkbox("Show Figures"):
            visualization_type = st.sidebar.radio(
                "Select visualization",
                ["Word cloud", "Word count distribution"]
                )
            if visualization_type == "Word cloud":
                st.sidebar.subheader("Word Cloud")
                wordcloud = WordCloud(
                     width=800,
                     height=400,
                     background_color='white',
                     stopwords=set(stopwords.words('english'))
                 ).generate(text)
                 
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.imshow(wordcloud)
                ax.axis('off')
                st.sidebar.pyplot(fig)
                plt.close()

            elif visualization_type == "Word count distribution":
                st.sidebar.subheader("Word count distribution")
                sections = text.split('\n\n')
                word_counts = {}
                for i, section in enumerate(sections, 1):
                    if section.strip():
                        word_counts[f"Section {i}"] = len(word_tokenize(section))

                visualizer = Visualizer()
                visualizer.plot_word_count_distribution(word_counts)

if __name__ == "__main__":
    main()
