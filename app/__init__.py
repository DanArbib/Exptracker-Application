from flask import Flask
from .extensions import db
from dotenv import load_dotenv
import os
import logging
from pythonjsonlogger import jsonlogger
from .models.user import User
from flask_bcrypt import Bcrypt
from prometheus_flask_exporter import PrometheusMetrics
load_dotenv()

FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
POSTGRES_DB = os.environ.get('POSTGRES_DB')
PG_HOST = os.environ.get('PG_HOST')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
PG_PORT = os.environ.get('PG_PORT', 5432)

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# App config
logger.info('Initializing Flask app')
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# Bcrypt config
bcrypt_app = Bcrypt(app)

# Prometheus metrics config
metrics = PrometheusMetrics(app)
metrics.info('glivs_app', 'Application info', version='1.0.3')

# Postgres URI config
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{PG_HOST}:{PG_PORT}/{POSTGRES_DB}"


# Database initialization
logger.info('Initializing Flask-SQLAlchemy')
db.init_app(app)
with app.app_context():
    db.create_all()

# Import routes
logger.info('Importing routes')
from app import routes