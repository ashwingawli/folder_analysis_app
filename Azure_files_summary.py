import streamlit as st
import os
import PyPDF2
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version="2023-05-15",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def get_pdf_text(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def summarize_text(text, max_tokens=150):
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),  # Use the deployment name from .env
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": f"Please summarize the following text in about {max_tokens} tokens:\n\n{text}"}
        ],
        max_tokens=max_tokens,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

def main():
    st.title("PDF Summarizer using Azure OpenAI")
    
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