import streamlit as st
import os
import datetime
import magic
import pandas as pd
from docx import Document
from streamlit_echarts import st_echarts


def get_file_info(file_path):
    try:
        stat = os.stat(file_path)
        try:
            file_type = magic.from_file(file_path, mime=True)
        except:
            file_type = "Unknown"
        size = stat.st_size
        date_modified = datetime.datetime.fromtimestamp(stat.st_mtime)
        date_created = datetime.datetime.fromtimestamp(stat.st_ctime)
        
        authors, tags, title = "", "", ""
        
        # Extract metadata for specific file types (example for .docx)
        if file_path.lower().endswith('.docx'):
            try:
                doc = Document(file_path)
                core_properties = doc.core_properties
                authors = core_properties.author or ""
                title = core_properties.title or ""
                tags = ", ".join(core_properties.keywords) if core_properties.keywords else ""
            except:
                pass  # If there's an error reading the file, we'll just leave these fields empty

        return {
            "name": os.path.basename(file_path),
            "type": file_type,
            "size": size,
            "date_modified": date_modified,
            "date_created": date_created,
            "authors": authors,
            "tags": tags,
            "title": title
        }
    except PermissionError:
        return {
            "name": os.path.basename(file_path),
            "type": "Access Denied",
            "size": 0,
            "date_modified": datetime.datetime.now(),
            "date_created": datetime.datetime.now(),
            "authors": "",
            "tags": "",
            "title": ""
        }
    except Exception as e:
        return {
            "name": os.path.basename(file_path),
            "type": f"Error: {str(e)}",
            "size": 0,
            "date_modified": datetime.datetime.now(),
            "date_created": datetime.datetime.now(),
            "authors": "",
            "tags": "",
            "title": ""
        }

def analyze_folder(folder_path):
    total_size = 0
    file_count = 0
    dir_count = 0
    file_types = {}
    items_info = []

    for root, dirs, files in os.walk(folder_path):
        for name in dirs:
            dir_path = os.path.join(root, name)
            dir_info = get_file_info(dir_path)
            dir_info["type"] = "Folder"
            try:
                dir_info["num_files"] = len(os.listdir(dir_path))
            except:
                dir_info["num_files"] = "Access Denied"
            items_info.append(dir_info)
            dir_count += 1

        for name in files:
            file_path = os.path.join(root, name)
            file_info = get_file_info(file_path)
            items_info.append(file_info)
            file_count += 1
            total_size += file_info["size"]
            
            _, ext = os.path.splitext(name)
            file_types[ext] = file_types.get(ext, 0) + 1

    return {
        'total_size': total_size,
        'file_count': file_count,
        'dir_count': dir_count,
        'file_types': file_types,
        'items_info': items_info
    }

def main():
    st.set_page_config(page_title="Folder Analysis App", page_icon="🗂️", layout="wide")
    # Hide the Streamlit menu
    hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    </style>
    """
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    
    tbh_logo= "images/TBH_Logo.png"
    st.logo(tbh_logo)
    st.title("🗂️ Folder Analysis Application")

    folder_path = st.text_input("Enter the folder path to analyze:")
    
    if st.button("Analyze"):
        if not folder_path:
            st.error("Please enter a folder path.")
        elif not os.path.exists(folder_path):
            st.error(f"The folder '{folder_path}' does not exist.")
        else:
            with st.spinner("Analyzing folder..."):
                results = analyze_folder(folder_path)

            st.success("Analysis complete!")

            st.header("📜 Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Items", results['file_count'] + results['dir_count'])
            col2.metric("Files", results['file_count'])
            col3.metric("Directories", results['dir_count'])
            col4.metric("Total Size", f"{results['total_size'] / (1024*1024):.2f} MB")

            st.header("📁 Folder Contents")
            df = pd.DataFrame(results['items_info'])
            df['size'] = df['size'].apply(lambda x: f"{x / 1024:.2f} KB")
            df['date_modified'] = df['date_modified'].dt.strftime('%Y-%m-%d %H:%M:%S')
            df['date_created'] = df['date_created'].dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(df, use_container_width=True)

            st.header("📚 File Types")
            file_types_data = [{"name": ext or "No extension", "value": count} for ext, count in results['file_types'].items()]
            options = {
                "tooltip": {"trigger": "item"},
                "legend": {"top": "5%", "left": "center"},
                "series": [{
                    "name": "File Types",
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "avoidLabelOverlap": False,
                    "itemStyle": {
                        "borderRadius": 10,
                        "borderColor": "#fff",
                        "borderWidth": 2
                    },
                    "label": {"show": False, "position": "center"},
                    "emphasis": {
                        "label": {"show": True, "fontSize": "40", "fontWeight": "bold"}
                    },
                    "labelLine": {"show": False},
                    "data": file_types_data
                }]
            }
            st_echarts(options=options, height="400px")

if __name__ == "__main__":
    main()