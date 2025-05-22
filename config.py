import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    TEMP_FOLDER = os.path.join(os.path.dirname(__file__), 'temp')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB upload limit
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

DEVICE = 'cpu'