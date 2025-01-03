import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Check if running inside a Docker container
def is_running_in_docker():
    if os.path.exists('/proc/self/cgroup'):
        with open('/proc/self/cgroup', 'rt') as f:
            return 'docker' in f.read()
    return False

# Set the database URL based on environment
if is_running_in_docker():
    URL_DATABASE = os.getenv("DOCKER_DATABASE_URL")
else:
    URL_DATABASE = os.getenv("DATABASE_URL")

# Ensure URL_DATABASE is set
if not URL_DATABASE:
    raise ValueError("DATABASE_URL is not set. Please provide a valid database connection string.")

# Debugging: Print the database URL (remove in production)
print(f"DATABASE_URL: {URL_DATABASE}")

# Initialize SQLAlchemy engine and session
engine = create_engine(
    URL_DATABASE, 
    pool_pre_ping=True   # Ensures connections are checked before use
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


