import streamlit as st
import os
import PyPDF2
from transformers import pipeline

# Set up the summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def get_pdf_text(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def summarize_text(text, max_length=150):
    summary = summarizer(text, max_length=max_length, min_length=30, do_sample=False)
    return summary[0]['summary_text']

def main():
    st.title("Files Summarizer")
    
    folder_path = st.text_input("Enter the path to the folder containing PDFs:")
    
    if folder_path and os.path.isdir(folder_path):
        pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
        
        if pdf_files:
            st.write(f"Found {len(pdf_files)} PDF files in the folder.")
            
            for pdf_file in pdf_files:
                pdf_path = os.path.join(folder_path, pdf_file)
                st.subheader(f"Summary of {pdf_file}")
                
                try:
                    pdf_text = get_pdf_text(pdf_path)
                    summary = summarize_text(pdf_text)
                    st.write(summary)
                except Exception as e:
                    st.error(f"Error processing {pdf_file}: {str(e)}")
        else:
            st.warning("No PDF files found in the specified folder.")
    elif folder_path:
        st.error("Invalid folder path. Please enter a valid path.")

if __name__ == "__main__":
    main()