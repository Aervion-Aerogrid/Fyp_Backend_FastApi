from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os
router = APIRouter()
# Load environment variables from .env file
load_dotenv()


# Global variable to hold the received data type
received_data_type: str = "synop"  # Default data type

# Request model for the data type
class DataTypeRequest(BaseModel):
    datatype: str

@router.post("/data-type", response_model=dict, status_code=201)
async def receive_data_type(data: DataTypeRequest):
    global received_data_type  # Declare the global variable
    received_data_type = data.datatype  # Update the data type
    print(f"Received data type: {received_data_type}")
    return {"message": "Data type received successfully", "datatype": received_data_type}

@router.get("/image-data")
def get_image_data(
    image_type: str = Query(..., description="Type of image requested (e.g., 'isobar', 'isotherm', 'isoneph')")
):
    
    # Get the proxy_url from the environment variables
    #proxy_url = 'https://awzzmmpi4a.execute-api.ap-south-1.amazonaws.com'
    proxy_url = 'http://localhost:8000'
    #os.getenv('PROXY_URL')
    # Check if the current data type is 'synop'
    if received_data_type == "synop":
        if not proxy_url:
           return JSONResponse(content={"error": "Proxy URL is not configured"}, status_code=500)
        # Hardcoded URLs for the images
        if image_type == "isobar":
            layer_image_url = f"{proxy_url}/assets/isobars.png"
            heatmap_image_url = f"{proxy_url}/assets/isobar_heatmap.png"
        elif image_type == "isotherm":
            layer_image_url = f"{proxy_url}/assets/isotherms.png"
            heatmap_image_url = f"{proxy_url}/assets/isotherm_heatmap.png"
        elif image_type == "isoneph":
            layer_image_url = f"{proxy_url}/assets/isonephs.png"
            heatmap_image_url = f"{proxy_url}/assets/isoneph_heatmap.png"
        elif image_type == "isotach":
            layer_image_url = f"{proxy_url}/assets/isotachs.png"
            heatmap_image_url = f"{proxy_url}/assets/isotach_heatmap.png"
        elif image_type == "isohume":
            layer_image_url = f"{proxy_url}/assets/isohumes.png"
            heatmap_image_url = f"{proxy_url}/assets/isohume_heatmap.png"
        elif image_type == "isogon":
            layer_image_url = f"{proxy_url}/assets/isogons.png"
            heatmap_image_url = f"{proxy_url}/assets/isogon_heatmap.png"
        elif image_type == "isohyet":
            layer_image_url = f"{proxy_url}/assets/isohyets.png"
            heatmap_image_url = f"{proxy_url}/assets/isohyet_heatmap.png"
        elif image_type == "isodrosotherm":
            layer_image_url = f"{proxy_url}/assets/isodrosotherms.png"
            heatmap_image_url = f"{proxy_url}/assets/isodrosotherm_heatmap.png"
        else:
            return JSONResponse(content={"error": "Invalid image type"}, status_code=400)
              

        # Define coordinates (bounds)
        coordinates = {
            "bounds": [
                [60.87, 23.63],
                [77.05, 37.23]
            ]
        }

        # Construct the response data
        data = {
            "layer_image_url": layer_image_url,
            "heatmap_image_url": heatmap_image_url,
            "coordinates": coordinates
        }

        return JSONResponse(content=data)

    # Handle the cases for 'metar' and 'wis2'
    elif received_data_type in ["metar", "wis2"]:
        return JSONResponse(content={"error": "No image data available for the requested data type."}, status_code=204)

    # If the data type is not recognized
    return JSONResponse(content={"error": "Invalid data type."}, status_code=400)

