import os
from flask import Flask

app = Flask(__name__)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    TEMP_FOLDER = os.path.join(app.root_path, 'static', 'temp')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB upload limit
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

DEVICE = 'cpu'