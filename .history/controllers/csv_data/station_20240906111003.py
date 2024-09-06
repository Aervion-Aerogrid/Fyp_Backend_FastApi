from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()

# Get the base directory dynamically, which works inside Docker and outside
BASE_DIR = os.getenv("BASE_DIR", os.getcwd())  # Default to current directory if no env variable

@router.get("/csv", response_class=FileResponse)
def get_station_csv():
    # Construct the file path for the CSV file
    filename = "station.csv"
    file_path = os.path.join(BASE_DIR, "assets", filename)  # Adjust this as needed

    # Check if the file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    return FileResponse(file_path, media_type="text/csv", filename="data.csv")
