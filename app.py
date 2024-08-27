import os
import datetime

def analyze_folder(folder_path, indent=""):
    total_size = 0
    file_count = 0
    dir_count = 0
    file_types = {}
    newest_item = None
    oldest_item = None

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        
        if os.path.isfile(item_path):
            file_count += 1
            size = os.path.getsize(item_path)
            total_size += size
            
            _, ext = os.path.splitext(item)
            file_types[ext] = file_types.get(ext, 0) + 1
            
            print(f"{indent}{item} ({size / 1024:.2f} KB)")
        
        elif os.path.isdir(item_path):
            dir_count += 1
            print(f"{indent}{item}/ (Directory)")
            sub_stats = analyze_folder(item_path, indent + "  ")
            
            total_size += sub_stats['total_size']
            file_count += sub_stats['file_count']
            dir_count += sub_stats['dir_count']
            
            for ext, count in sub_stats['file_types'].items():
                file_types[ext] = file_types.get(ext, 0) + count
        
        mod_time = os.path.getmtime(item_path)
        if newest_item is None or mod_time > os.path.getmtime(os.path.join(folder_path, newest_item)):
            newest_item = item
        if oldest_item is None or mod_time < os.path.getmtime(os.path.join(folder_path, oldest_item)):
            oldest_item = item

    if indent == "":  # Only print summary for the top-level call
        print(f"\nFolder analysis for: {folder_path}")
        print(f"Total items: {file_count + dir_count}")
        print(f"Files: {file_count}")
        print(f"Directories: {dir_count}")
        print(f"Total size: {total_size / (1024*1024):.2f} MB")
        print("\nFile types:")
        for ext, count in file_types.items():
            print(f"  {ext or 'No extension'}: {count}")
        print(f"\nNewest item: {newest_item} (modified {datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(folder_path, newest_item)))})")
        print(f"Oldest item: {oldest_item} (modified {datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(folder_path, oldest_item)))})")

    return {
        'total_size': total_size,
        'file_count': file_count,
        'dir_count': dir_count,
        'file_types': file_types,
        'newest_item': newest_item,
        'oldest_item': oldest_item
    }

# Example usage
folder_to_analyze = r"C:\Users\ashwin.gawli\OneDrive - TBH\Documents\Projects\ClaimsNDisputes\ClaimsndisputesGpt\Test Dataset - Dora Creek"  # Use 'r' prefix for raw string
analyze_folder(folder_to_analyze)