from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/csv", response_class=FileResponse)
def get_station_csv():
    # Construct the file path for the CSV file
    base_path = os.path.dirname(__file__) 
    filename = "station.csv"  # Replace with your actual CSV filename
    file_path = os.path.join("../../assets", filename)  # Correct file path

    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    return FileResponse(file_path, media_type="text/csv", filename="data.csv")
