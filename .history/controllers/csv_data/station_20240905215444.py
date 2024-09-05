from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/csv", response_class=FileResponse)
def get_station_csv():
    # Construct the file path for the CSV file
    filename = "station.csv"  # Replace with your actual CSV filename
    file_path = os.path.join(os.path.dirname(__file__), "http://localhost:8000/assets/", filename)

    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    return FileResponse(file_path, media_type="text/csv", filename="data.csv")