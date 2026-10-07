import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    """Smart Canteen System Configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-canteen-super-secret-key-2026-xyz987')
    
    # Database Configuration: 'postgres', 'mysql', 'sqlite', or 'auto'
    DB_TYPE = os.environ.get('DB_TYPE', 'auto')
    
    # PostgreSQL / pgAdmin Settings
    PG_HOST = os.environ.get('PG_HOST', 'localhost')
    PG_PORT = int(os.environ.get('PG_PORT', 5432))
    PG_USER = os.environ.get('PG_USER', 'postgres')
    PG_PASSWORD = os.environ.get('PG_PASSWORD', 'postgres')
    PG_DATABASE = os.environ.get('PG_DATABASE', 'smart_canteen')
    
    # MySQL Settings
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'smart_canteen')
    
    # SQLite Path
    SQLITE_PATH = os.path.join(BASE_DIR, 'database', 'smart_canteen.db')
    
    # Paths
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    REPORTS_FOLDER = os.path.join(BASE_DIR, 'reports')
    AI_MODELS_DIR = os.path.join(BASE_DIR, 'ai', 'saved_models')
    
    # Business Rules
    TAX_RATE = 0.05       # 5% GST
    PLATFORM_FEE = 0.0    # No platform fee for students
    BASE_PREP_BUFFER = 3  # 3 minutes base safety buffer for orders
    
    # Pagination
    ITEMS_PER_PAGE = 12
