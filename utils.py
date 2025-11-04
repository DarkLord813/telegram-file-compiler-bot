import os
import shutil
import time

def ensure_directory(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def cleanup_old_files(directory, max_age_hours=24):
    """Clean up files older than max_age_hours"""
    if not os.path.exists(directory):
        return
    
    current_time = time.time()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getctime(file_path)
            if file_age > max_age_hours * 3600:
                os.remove(file_path)

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def safe_filename(filename):
    """Make filename safe by removing special characters"""
    import re
    filename = re.sub(r'[^\w\.-]', '_', filename)
    return filename
