import os
import sqlite3
from pathlib import Path
from PIL import Image
import subprocess

# Define supported file extensions for images and videos
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv']

# Initialize database
def init_db(db_name="media.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS media (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_name TEXT,
                        file_path TEXT,
                        file_type TEXT,
                        width INTEGER,
                        height INTEGER,
                        duration REAL,
                        file_size INTEGER,
                        date_created TEXT
                    )''')
    conn.commit()
    return conn

# Insert media data into the database
def insert_media(conn, media_data):
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO media (file_name, file_path, file_type, width, height, duration, file_size, date_created)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', media_data)
    conn.commit()

# Get video metadata using ffprobe (ffmpeg tool)
def get_video_metadata(video_path):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,duration',
             '-of', 'default=noprint_wrappers=1', video_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        metadata = result.stdout.splitlines()
        width = int(metadata[0].split('=')[1])
        height = int(metadata[1].split('=')[1])
        duration = float(metadata[2].split('=')[1])
        return width, height, duration
    except Exception as e:
        print(f"Error getting video metadata: {e}")
        return None, None, None

# Get image metadata using PIL (Pillow)
def get_image_metadata(image_path):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            return width, height
    except Exception as e:
        print(f"Error getting image metadata: {e}")
        return None, None

# Process media files (images and videos) in the directory
def process_media_files(directory, conn):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            file_ext = file_path.suffix.lower()
            file_size = os.path.getsize(file_path)
            date_created = Path(file_path).stat().st_ctime

            if file_ext in IMAGE_EXTENSIONS:
                width, height = get_image_metadata(file_path)
                insert_media(conn, (file, str(file_path), 'image', width, height, None, file_size, date_created))

            elif file_ext in VIDEO_EXTENSIONS:
                width, height, duration = get_video_metadata(str(file_path))
                insert_media(conn, (file, str(file_path), 'video', width, height, duration, file_size, date_created))

# Main function
if __name__ == '__main__':
    media_directory = "path_to_your_media_folder"  # Set this to your media directory
    conn = init_db()
    process_media_files(media_directory, conn)
    conn.close()
    print("Media files processed and stored in the database.")
    