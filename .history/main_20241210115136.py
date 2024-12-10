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
from data_generation.get_data import fetch_weather_data
import time
from contextlib import asynccontextmanager
import schedule
import time
import subprocess
from datetime import datetime

app = FastAPI()
router = APIRouter()
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

db_dependency = Annotated[Session, Depends(get_db)]




# Admin creation
@app.post("/admin/", status_code=status.HTTP_201_CREATED)
async def create_admin_route(
    admin: AdminCreate, 
    db: Session = Depends(get_db), 
   
):
    result = create_admin(db, admin)  # Pass the background task to send email

    if result is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    return result


#Get access of username information
@app.get("/admin/{username}", response_model=UserResponse)
async def get_admin_by_username_route(username: str, db: db_dependency):
    admin = get_admin_by_username(db, username)
    
    if admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")

    return admin

# sending username and password from frontend and returning login success and message
@app.post("/admin/login", response_model=AdminResponse)
async def login_admin_route(admin: AdminLogin, db: Annotated[Session, Depends(get_db)]):
    return login_admin(db, admin)  # Call the login_admin function from crud.py



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
schedule.every().day.at("00:00").do(run_scripts)  # Midnight
schedule.every().day.at("03:30").do(run_scripts)
schedule.every().day.at("06:30").do(run_scripts)
schedule.every().day.at("09:30").do(run_scripts)
schedule.every().day.at("12:30").do(run_scripts)
schedule.every().day.at("15:30").do(run_scripts)
schedule.every().day.at("18:30").do(run_scripts)
schedule.every().day.at("21:30").do(run_scripts)

print("Scheduler started. Press Ctrl+C to exit.")

# Keep the scheduler running
while True:
    schedule.run_pending()  # Run pending tasks
    time.sleep(1)  # Sleep to prevent high CPU usage

