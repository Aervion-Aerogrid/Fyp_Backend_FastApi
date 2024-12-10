from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()

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
    # Check if the current data type is 'synop'
    if received_data_type == "synop":
        # Hardcoded URLs for the images
        if image_type == "isobar":
            layer_image_url = "http://localhost:8000/assets/isobars.png"
            heatmap_image_url = "http://localhost:8000/assets/isobar_heatmap.png"
        elif image_type == "isotherm":
            layer_image_url = "http://localhost:8000/assets/isotherms.png"
            heatmap_image_url = "http://localhost:8000/assets/isotherm_heatmap.png"
        elif image_type == "isoneph":
            layer_image_url = "http://localhost:8000/assets/isonephs.png"
            heatmap_image_url = "http://localhost:8000/assets/isoneph_heatmap.png"
        elif image_type == "isotach":
            layer_image_url = "http://localhost:8000/assets/isotachs.png"
            heatmap_image_url = "http://localhost:8000/assets/isotachs_heatmap.png"
        elif image_type == "isohume":
            layer_image_url = "http://localhost:8000/assets/isohumes.png"
            heatmap_image_url = "http://localhost:8000/assets/isohume_heatmap.png"
        elif image_type == "isogon":
            layer_image_url = "http://localhost:8000/assets/isogons.png"
            heatmap_image_url = "http://localhost:8000/assets/isogon_heatmap.png"
        elif image_type == "isohyet":
            layer_image_url = "http://localhost:8000/assets/isohyets.png"
            heatmap_image_url = "http://localhost:8000/assets/isohyet_heatmap.png"
        elif image_type == "isodrosotherm":
            layer_image_url = "http://localhost:8000/assets/isodrosotherms.png"
            heatmap_image_url = "http://localhost:8000/assets/isodrosotherm_heatmap.png"
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

