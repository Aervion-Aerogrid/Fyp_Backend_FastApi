from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
from controllers.geojson_data.isobars import router as isobar_router  
from controllers.csv_data.station import router as csv_data
from controllers.image_data.images import router as image_data
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()
router = APIRouter()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, change to specific origins for production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def root():
    return {"message": "Hello World"}

# Include the isobar router
app.include_router(isobar_router)
app.include_router(csv_data)
app.include_router(image_data)
# Static files serving
app.mount("/assets", StaticFiles(directory="../assets"), name="assets")  # Ensure this path is correct
