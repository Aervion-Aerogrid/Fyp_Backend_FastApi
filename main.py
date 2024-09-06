from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from controllers.csv_data.station import router as csv_data
from controllers.image_data.images import router as image_data


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


# Station data is in csv
app.include_router(csv_data)
app.include_router(image_data)
# Static files serving
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
