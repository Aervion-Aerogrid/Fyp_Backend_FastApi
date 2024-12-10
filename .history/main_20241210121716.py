import subprocess
import threading
from fastapi import FastAPI, HTTPException, Depends,status
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from requests_cache import Optional
from controllers.csv_data.station import router as csv_data
from controllers.image_data.images import router as image_data
from typing import Annotated
from functionality.login import AdminLogin, AdminResponse, UserResponse, get_admin_by_username, login_admin
from functionality.signup import AdminCreate, create_admin
import models 
from database import engine,SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import HTTPException, status, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi import FastAPI, BackgroundTasks, status
# Import the Admin model from models.py
from models import Admin, DataTypeRequest  # <-- Import your models here
from sqlalchemy import text
# Import the function from get_data.py
import time
from contextlib import asynccontextmanager
import schedule
import time
import subprocess
from datetime import datetime

import threading
import subprocess
import schedule
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from models import Admin, DataTypeRequest  # Your models here
from database import engine, SessionLocal
from controllers.csv_data.station import router as csv_data
from controllers.image_data.images import router as image_data

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello World"}

# Include other routers
app.include_router(csv_data)
app.include_router(image_data)

# Static files serving
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Admin creation and other routes ...

def run_scripts():
    print(f"Running scripts at {datetime.now()}")

    # List of scripts to execute
    scripts = [
        "./data_generation/get_data.py",
        "./data_generation/process_data.py",
        "./data_generation/filter_data.py",
        "./data_generation/isobar.py",
        "./data_generation/isotherm.py",
        "./data_generation/isohume.py",
        "./data_generation/isotach.py",
        "./data_generation/isogon.py",
    ]

    for script in scripts:
        try:
            subprocess.run(["python", script], check=True)
            print(f"{script} executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error while executing {script}: {e}")

# Schedule the task to run at the specified times
def schedule_tasks():
    schedule.every().day.at("00:00").do(run_scripts)  # Midnight
    schedule.every().day.at("03:30").do(run_scripts)
    schedule.every().day.at("06:30").do(run_scripts)
    schedule.every().day.at("09:30").do(run_scripts)
    schedule.every().day.at("12:30").do(run_scripts)
    schedule.every().day.at("15:30").do(run_scripts)
    schedule.every().day.at("18:30").do(run_scripts)
    schedule.every().day.at("21:30").do(run_scripts)

    print("Scheduler started. Press Ctrl+C to exit.")

    # Keep the scheduler running in the background
    while True:
        schedule.run_pending()  # Run pending tasks
        time.sleep(1)  # Sleep to prevent high CPU usage

# Run the scheduler in a separate thread
scheduler_thread = threading.Thread(target=schedule_tasks)
scheduler_thread.daemon = True
scheduler_thread.start()


