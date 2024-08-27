import streamlit as st
import os
import datetime
from streamlit_echarts import st_echarts

def analyze_folder(folder_path):
    total_size = 0
    file_count = 0
    dir_count = 0
    file_types = {}
    newest_item = None
    oldest_item = None
    tree_structure = []

    for root, dirs, files in os.walk(folder_path):
        level = root.replace(folder_path, '').count(os.sep)
        indent = '&nbsp;' * 4 * level
        folder_name = os.path.basename(root)
        tree_structure.append(f"{indent}📁 **{folder_name}/**")
        dir_count += 1

        for file in files:
            file_count += 1
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            total_size += size
            
            _, ext = os.path.splitext(file)
            file_types[ext] = file_types.get(ext, 0) + 1
            
            tree_structure.append(f"{indent}&nbsp;&nbsp;&nbsp;&nbsp;📄 {file} ({size / 1024:.2f} KB)")
        
            mod_time = os.path.getmtime(file_path)
            if newest_item is None or mod_time > os.path.getmtime(newest_item):
                newest_item = file_path
            if oldest_item is None or mod_time < os.path.getmtime(oldest_item):
                oldest_item = file_path

    return {
        'total_size': total_size,
        'file_count': file_count,
        'dir_count': dir_count,
        'file_types': file_types,
        'newest_item': newest_item,
        'oldest_item': oldest_item,
        'tree_structure': tree_structure
    }

def main():
    st.set_page_config(page_title="Folder Analysis App", page_icon="📊", layout="wide")
    st.title("📊 Folder Analysis App")

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

            col1, col2 = st.columns(2)

            with col1:
                st.header("📁 Folder Structure")
                st.markdown("\n".join(results['tree_structure']), unsafe_allow_html=True)

            with col2:
                st.header("📊 Summary")
                st.info(f"📚 Total items: {results['file_count'] + results['dir_count']}")
                st.info(f"📄 Files: {results['file_count']}")
                st.info(f"📁 Directories: {results['dir_count']}")
                st.info(f"💾 Total size: {results['total_size'] / (1024*1024):.2f} MB")

                st.header("📊 File Types")
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

            st.header("🕒 Newest and Oldest Items")
            st.success(f"✨ Newest item: {os.path.basename(results['newest_item'])} "
                       f"(modified {datetime.datetime.fromtimestamp(os.path.getmtime(results['newest_item']))})")
            st.warning(f"🏛️ Oldest item: {os.path.basename(results['oldest_item'])} "
                       f"(modified {datetime.datetime.fromtimestamp(os.path.getmtime(results['oldest_item']))})")

if __name__ == "__main__":
    main()