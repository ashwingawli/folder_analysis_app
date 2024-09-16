import streamlit as st
import os
import PyPDF2
from openai import AzureOpenAI
from dotenv import load_dotenv
import pandas as pd

# Specify the path to your .env file
env_path = os.path.join(os.path.dirname(__file__), '..', 'config', '.env')

# Load environment variables from the specified path
load_dotenv(dotenv_path=env_path)

# st.write(f"Using .env file from: {env_path}")

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
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": f"Please summarize the following text in about {max_tokens} tokens:\n\n{text}"}
        ],
        max_tokens=max_tokens,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

def get_pdf_files(folder_path):
    pdf_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def main():
    st.title("Files Summarizer using TBH-Azure OpenAI")
    
    folder_path = st.text_input("Enter the path to the folder:")
    
    if folder_path and os.path.isdir(folder_path):
        pdf_files = get_pdf_files(folder_path)
        
        if pdf_files:
            st.write(f"Found {len(pdf_files)} PDF files in the folder and its subfolders.")
            
            summaries = []
            
            progress_bar = st.progress(0)
            for i, pdf_path in enumerate(pdf_files):
                try:
                    pdf_text = get_pdf_text(pdf_path)
                    summary = summarize_text(pdf_text)
                    relative_path = os.path.relpath(pdf_path, folder_path)
                    summaries.append({
                        "File Name": os.path.basename(pdf_path),
                        "Relative Path": relative_path,
                        "Summary": summary
                    })
                except Exception as e:
                    st.error(f"Error processing {pdf_path}: {str(e)}")
                progress_bar.progress((i + 1) / len(pdf_files))
            
            # Create a DataFrame and display it
            df = pd.DataFrame(summaries)
            st.dataframe(df)
            
            # Option to download the summary as a CSV file
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download summaries as CSV",
                data=csv,
                file_name="pdf_summaries.csv",
                mime="text/csv",
            )
        else:
            st.warning("No PDF files found in the specified folder or its subfolders.")
    elif folder_path:
        st.error("Invalid folder path. Please enter a valid path.")

if __name__ == "__main__":
    main()